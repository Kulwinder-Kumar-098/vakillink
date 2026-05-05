import json
import hashlib
from groq import Groq
import google.generativeai as genai
from .retrieval_from_qdrant import LegalRetriever
from app.core.config import settings

_cache = {}

def get_cached(query: str):
    key = hashlib.md5(query.lower().strip().encode()).hexdigest()
    return _cache.get(key)

def set_cache(query: str, response: dict):
    key = hashlib.md5(query.lower().strip().encode()).hexdigest()
    _cache[key] = response

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL   = "llama-3.3-70b-versatile"
GOOGLE_API_KEY = settings.GOOGLE_API_KEY

class LegalQAEngine:
    def __init__(self, retriever=None):
        self.retriever = retriever or LegalRetriever()
        self.groq_client = Groq(api_key=GROQ_API_KEY)
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
        
    def ask(self, query: str):
        cached = get_cached(query)
        if cached:
            print(f"\n[AI] Returning cached response for query: {query}...")
            return cached

        print(f"\n[AI] Processing query: {query}...")
        
        # 1. Retrieve context
        results = self.retriever.search(query, score_threshold=0.35)
        
        # 2. Construct Prompt
        context_blocks = []
        if results:
            for i, res in enumerate(results):
                # Trim chunk text to 3 sentences
                sentences = [s.strip() for s in res['chunk_text'].split('.') if s.strip()]
                trimmed_chunk = '. '.join(sentences[:3]) + ('.' if sentences else '')
                block = (
                    f"DOCUMENT {i+1}\n"
                    f"SOURCE: {res['law_name']} ({res['domain']})\n"
                    f"LEGAL ISSUE: {res['legal_issue']}\n"
                    f"RELEVANT ACTS/SECTIONS: {res['acts']} | {res['sections']}\n"
                    f"EXCERPT: {trimmed_chunk}\n"
                )
                context_blocks.append(block)
        
        context_text = "\n".join(context_blocks) if context_blocks else "No specific legal precedents found in the database. Provide general legal guidance based on Indian law."
        
        system_msg = (
            "You are an expert Indian Legal Assistant. Your task is to provide a concise and accurate analysis of the user's query.\n"
            "Use the provided LEGAL CONTEXT EXCERPTS to support your answer if available. If not, rely on your knowledge of Indian law.\n"
            "Output MUST be in valid JSON format with the following keys:\n"
            "- domain: The specific legal domain (e.g., Criminal, Civil, Constitutional)\n"
            "- analysis: A 2-3 sentence legal analysis including a disclaimer.\n"
            "- cited_sections: List of specific legal sections mentioned.\n"
            "- cited_cases: List of relevant court cases.\n"
            "- cited_acts: List of relevant Indian Acts.\n"
            "- confidence: A float between 0 and 1 indicating your confidence.\n"
            "Be specific and avoid generic answers."
        )
        
        user_msg = f"USER QUERY: {query}\n\nLEGAL CONTEXT EXCERPTS:\n{context_text}"
        
        # 3. Generate Answer (Try Groq first, then Gemini)
        response_data = None
        
        # Try Groq
        try:
            print("[AI] Attempting generation with Groq...")
            completion = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            response_data = json.loads(completion.choices[0].message.content)
        except Exception as groq_err:
            print(f"[AI] Groq failed: {groq_err}. Falling back to Gemini...")
            if self.gemini_model:
                try:
                    prompt = f"{system_msg}\n\n{user_msg}"
                    gemini_res = self.gemini_model.generate_content(prompt)
                    # Extract JSON from Gemini response
                    text = gemini_res.text
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()
                    response_data = json.loads(text)
                except Exception as gemini_err:
                    print(f"[AI] Gemini also failed: {gemini_err}")
            
        if not response_data:
            # Absolute fallback
            response_data = {
                "analysis": "I'm sorry, I'm currently unable to process your request due to technical difficulties. Please try again later. (Disclaimer: Not legal advice)",
                "domain": "error",
                "cited_sections": [],
                "cited_cases": [],
                "cited_acts": [],
                "confidence": 0.0
            }

        # Calculate confidence score based on retrieval
        if results:
            top_results = results[:3]
            conf_score = sum(r.get('score', 0) for r in top_results) / len(top_results)
        else:
            conf_score = response_data.get("confidence", 0.5)
            
        response_data["confidence_score"] = conf_score
        
        final_response = {
            **response_data,
            "citations": results or []
        }
        
        set_cache(query, final_response)
        return final_response

if __name__ == "__main__":
    engine = LegalQAEngine()
    query = "What are the rights of manual scavengers under the Indian Constitution?"
    answer = engine.ask(query)
    print("\n" + "="*50)
    print("LEGAL ANALYSIS")
    print("="*50)
    print(answer)
    print("="*50)
