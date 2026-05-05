import os
import numpy as np
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
QDRANT_URL     = "https://dd8cf751-1ca8-46fa-8c89-f1f6c6961784.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6M2EyMzM4ZDQtNzRjZC00ZGViLTgwMjYtODY2OTkwODg5YmY1In0.hDm23QaqaDxj1yWYhsaIa77V6wB6ij-LaMdM69QzWaM"
MODEL_NAME     = "sentence-transformers/all-MiniLM-L6-v2"

# ─────────────────────────────────────────────
# DOMAIN CLASSIFIER (KEYWORD-BASED)
# ─────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    "legal_constitutional": {
        "primary": ["article 17", "article 21", "fundamental rights", "manual scavenger", "untouchability", "writ petition", "puttaswamy"],
        "secondary": ["dignity", "equality", "constitution"]
    },
    "legal_criminal": {
        "primary": ["bail", "fir", "ipc", "crpc", "murder", "theft", "arrest", "custody",
                    "cheque bounce", "section 138", "negotiable instruments", "dishonour",
                    "cybercrime", "it act", "section 66", "498a", "cruelty", "dowry"],
        "secondary": ["offence", "accused", "criminal"]
    },
    "legal_labour": {
        "primary": ["employment", "wages", "workmen", "labour court", "retrenchment", 
                    "industrial disputes", "posh act", "sexual harassment", "maternity benefit"],
        "secondary": ["worker", "employer", "compensation"]
    },
    "legal_consumer": {
        "primary": ["consumer complaint", "deficiency of service", "ncdrc", 
                    "district forum", "consumer court", "consumer protection",
                    "rera", "possession delay", "medical negligence", "flight cancellation", "online refund"],
        "secondary": ["insurance", "refund", "manufacturer", "service provider"]
    },
    "legal_motor_accident": {
        "primary": ["motor accident", "mact", "hit and run", "vehicle collision",
                    "motor vehicle", "accident claim", "motor insurance", "compensation multiplier", "loss of income"],
        "secondary": ["tribunal", "compensation", "rash driving"]
    },
    "legal_family": {
        "primary": ["divorce", "maintenance", "custody", "hindu marriage", "section 13"],
        "secondary": ["cruelty", "alimony", "spouse"]
    }
}

DOMAIN_DESCRIPTIONS = {
    "legal_constitutional": "fundamental rights constitution article writ",
    "legal_criminal": "crime bail arrest FIR punishment offence",
    "legal_consumer": "consumer complaint deficiency service product",
    "legal_family": "marriage divorce custody maintenance family",
    "legal_labour": "employment wages worker termination labour",
    "legal_motor_accident": "accident vehicle compensation motor MACT"
}

DOMAIN_PRIORITY = [
    "legal_constitutional", 
    "legal_criminal",
    "legal_consumer", 
    "legal_family",
    "legal_labour",
    "legal_motor_accident"
]

# ─────────────────────────────────────────────
# RETRIEVAL ENGINE
# ─────────────────────────────────────────────
from numpy.linalg import norm
def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

class LegalRetriever:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.model = SentenceTransformer(MODEL_NAME)
        
    def classify_domain(self, query: str) -> List[str]:
        query_lower = query.lower()
        domain_scores = {}
        
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = 0
            score += sum(3 for kw in keywords["primary"] if kw in query_lower)    # primary = 3pts
            score += sum(1 for kw in keywords["secondary"] if kw in query_lower)  # secondary = 1pt
            if score > 0:
                domain_scores[domain] = score
        
        if not domain_scores:
            query_embedding = self.model.encode(query)
            best_domain = max(
                DOMAIN_DESCRIPTIONS.keys(),
                key=lambda d: cosine_similarity(
                    query_embedding, 
                    self.model.encode(DOMAIN_DESCRIPTIONS[d])
                )
            )
            return [best_domain]
        
        max_score = max(domain_scores.values())
        matched_domains = [d for d, s in domain_scores.items() if s >= max_score - 3]
        
        if len(matched_domains) <= 1:
            return matched_domains
            
        matched_domains.sort(key=lambda d: DOMAIN_PRIORITY.index(d) if d in DOMAIN_PRIORITY else 99)
        return matched_domains[:2]

    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.35):
        import re
        print(f"\n[QUERY] {query}")
        
        # 1. Classify
        target_collections = self.classify_domain(query)
        print(f"[DOMAINS] {target_collections}")
        
        # 2. Embed
        query_vec = self.model.encode(query).tolist()
        
        # 3. Extract citations for hybrid boosting
        citations = re.findall(r'article \d+|section \d+|crpc \d+|ipc \d+', query.lower())
        if citations:
            print(f"[CITATIONS DETECTED] {citations}")
        
        # 4. Search across collections
        all_results = []
        for coll in target_collections:
            try:
                search_result = self.client.query_points(
                    collection_name=coll,
                    query=query_vec,
                    limit=top_k * 2,  # Fetch more for diversity
                    with_payload=True
                ).points
                
                for res in search_result:
                    score = res.score
                    
                    # Problem 2: Hybrid Citation Boost
                    chunk_text = res.payload.get("chunk_text", "").lower()
                    if citations:
                        citation_boost = sum(0.15 for c in citations if c in chunk_text)
                        score += citation_boost
                    
                    if score >= score_threshold:
                        all_results.append({
                            "chunk_text": res.payload.get("chunk_text", ""),
                            "score": score,
                            "domain": coll,
                            "subdomain": res.payload.get("subdomain", ""),
                            "law_name": res.payload.get("law_name", ""),
                            "legal_issue": res.payload.get("legal_issue", ""),
                            "sections": res.payload.get("sections", ""),
                            "acts": res.payload.get("acts", ""),
                        })
            except Exception as e:
                print(f"[WARN] Failed to search {coll}: {e}")
                
        # 5. Global Rerank (Simple Score Sort)
        all_results = sorted(all_results, key=lambda x: x["score"], reverse=True)
        
        # 6. MMR (Maximal Marginal Relevance) for diversity
        final_results = self.apply_mmr(all_results, top_k)
        
        return final_results

    def apply_mmr(self, results: List[Dict], top_k: int, lambda_param: float = 0.5):
        """Simple MMR to prevent returning the same case multiple times."""
        if not results: return []
        
        selected = []
        seen_cases = set()
        
        for res in results:
            case = res["law_name"]
            if case not in seen_cases:
                selected.append(res)
                seen_cases.add(case)
            if len(selected) >= top_k:
                break
                
        return selected

# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    retriever = LegalRetriever()
    
    test_queries = [
        "rights of manual scavengers",
        "how to file a FIR for assault?",
        "compensation for motor accident",
        "divorce procedure in India"
    ]
    
    for q in test_queries:
        results = retriever.search(q)
        print(f"Results for: {q}")
        for i, res in enumerate(results):
            print(f"  {i+1}. [Score: {res['score']:.4f}] Case: {res['law_name']}")
            print(f"     Domain: {res['domain']} | Subdomain: {res['subdomain']}")
            print(f"     Legal Issue: {res['legal_issue']}")
            print(f"     Acts: {res['acts']} | Sections: {res['sections']}")
            # Truncate text for display
            text_preview = res['chunk_text'][:200].replace('\n', ' ') + "..."
            print(f"     Text: {text_preview}\n")