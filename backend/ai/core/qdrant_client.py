from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from ai.core.config import settings
from ai.core.embedder import embedder
import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# Shared client — one connection pool for the whole app
_client: QdrantClient | None = None

# Domain priority for sorting results
DOMAIN_PRIORITY = [
    "legal_constitutional", 
    "legal_criminal",
    "legal_consumer", 
    "legal_family",
    "legal_labour",
    "legal_motor_accident"
]

# Collection names as defined in upload_to_qdrant.py
COLLECTIONS = [
    "legal_criminal",
    "legal_constitutional",
    "legal_consumer",
    "legal_family",
    "legal_labour",
    "legal_motor_accident",
    "legal_general"
]

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        logger.info(f"Connected to Qdrant: {settings.QDRANT_URL}")
    return _client


def retrieve_chunks(
    query: str,
    top_k: int = None,
    doc_type_filter: str | None = None,
) -> list[dict]:
    """
    Embed the query, search across all legal collections in Qdrant, return ranked chunks.
    """
    k = top_k or settings.TOP_K_RESULTS
    client = get_qdrant_client()

    # Step 1: Embed query
    vector = embedder.embed(query)

    # Step 2: Extract citations for hybrid boosting
    citations = re.findall(r'article \d+|section \d+|crpc \d+|ipc \d+', query.lower())

    all_results = []
    
    # Step 3: Search across all available collections
    for collection in COLLECTIONS:
        try:
            # Check if collection exists to avoid 404
            if not client.collection_exists(collection):
                continue

            hits = client.search(
                collection_name=collection,
                query_vector=vector,
                limit=k,
                score_threshold=settings.SIMILARITY_THRESHOLD,
                with_payload=True,
            )

            for hit in hits:
                score = hit.score
                payload = hit.payload or {}
                
                # Apply citation boost if matched in chunk_text
                chunk_text = payload.get("chunk_text", "").lower()
                if citations:
                    citation_boost = sum(0.15 for c in citations if c in chunk_text)
                    score += citation_boost

                all_results.append({
                    "id": str(hit.id),
                    "score": round(score, 4),
                    "text": payload.get("chunk_text", ""),
                    "metadata": {
                        "source": payload.get("law_name", "Unknown"),
                        "domain": payload.get("domain", collection),
                        "legal_issue": payload.get("legal_issue", ""),
                        "acts": payload.get("acts", ""),
                        "sections": payload.get("sections", ""),
                        "year": payload.get("year", ""),
                        "subdomain": payload.get("subdomain", "")
                    }
                })
        except Exception as e:
            logger.error(f"Error searching collection {collection}: {e}")
            continue

    # Step 4: Sort all results by score and limit
    all_results.sort(key=lambda x: x["score"], reverse=True)
    results = all_results[:k]

    logger.info(f"Retrieved {len(results)} chunks across collections for query: '{query[:60]}...'")
    return results
