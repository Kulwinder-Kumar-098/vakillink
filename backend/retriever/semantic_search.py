"""
retriever/semantic_search.py
FAISS-backed semantic search over the Vakilink legal corpus.

Features:
  - Lazy index loading (loaded once, cached in module)
  - Domain filtering post-retrieval
  - Score normalisation to [0, 1]
  - Structured result dicts compatible with the API layer
"""
from __future__ import annotations

import threading
from typing import List, Optional

import faiss
import numpy as np

from pipeline.embedding import embed_query
from pipeline.indexing import load_index, index_exists
from utils.config import settings, FAISS_INDEX_PATH, FAISS_META_PATH
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Module-level singleton (thread-safe) ──────────────────────────────────────
_index:  faiss.IndexFlatIP | None = None
_chunks: List[dict]               = []
_lock    = threading.Lock()


def _ensure_loaded() -> None:
    """Load the FAISS index and metadata exactly once."""
    global _index, _chunks
    if _index is not None:
        return
    with _lock:
        if _index is not None:
            return
        if not index_exists():
            raise RuntimeError(
                "FAISS index not found. Run 'python run_indexing.py' first."
            )
        _index, _chunks = load_index(FAISS_INDEX_PATH, FAISS_META_PATH)
        logger.info(f"Retriever ready: {_index.ntotal} vectors loaded.")


# ── Public API ────────────────────────────────────────────────────────────────

def semantic_search(
    query:         str,
    top_k:         int            = None,
    domain_filter: Optional[str]  = None,
    score_threshold: float        = None,
) -> List[dict]:
    """
    Perform semantic search over the FAISS index.

    Args:
        query:           Natural-language legal query.
        top_k:           Number of results to return (default from config).
        domain_filter:   If set, only return chunks where chunk.domain == value.
        score_threshold: Minimum cosine similarity (0-1) to include a result.

    Returns:
        List of result dicts sorted by score descending.
    """
    _ensure_loaded()

    k         = top_k          or settings.TOP_K_RESULTS
    threshold = score_threshold or settings.SIMILARITY_THRESHOLD

    # Embed query → shape (1, dim)
    query_vec = embed_query(query)

    # Search — retrieve extra candidates to allow for domain filtering
    search_k  = k * 4 if domain_filter else k * 2
    search_k  = min(search_k, _index.ntotal)

    scores, indices = _index.search(query_vec, search_k)
    scores   = scores[0]    # flatten (1, k) → (k,)
    indices  = indices[0]

    results: List[dict] = []

    for score, idx in zip(scores, indices):
        if idx < 0:             # FAISS padding for empty slots
            continue
        if score < threshold:
            break               # sorted descending — no point continuing

        chunk = _chunks[idx]

        # Apply domain filter
        if domain_filter and chunk.get("domain", "").lower() != domain_filter.lower():
            continue

        results.append({
            "chunk_id":    chunk.get("chunk_id", str(idx)),
            "score":       round(float(score), 4),
            "text":        chunk.get("text", ""),
            "case_name":   chunk.get("case_name", "Unknown"),
            "domain":      chunk.get("domain", "general"),
            "subdomain":   chunk.get("subdomain", ""),
            "legal_issue": chunk.get("legal_issue", ""),
            "source":      chunk.get("source", ""),
            "acts":        chunk.get("acts", ""),
            "sections":    chunk.get("sections", ""),
            "year":        chunk.get("year", ""),
            "court":       chunk.get("court", "N/A"),
        })

        if len(results) >= k:
            break

    logger.info(
        f"Search: '{query[:60]}' → {len(results)} results "
        f"(domain={domain_filter or 'all'})"
    )
    return results


def get_available_domains() -> List[str]:
    """Return sorted list of unique domain values from loaded metadata."""
    _ensure_loaded()
    return sorted({c.get("domain", "") for c in _chunks if c.get("domain")})


def reload_index() -> None:
    """Force a fresh reload of the index (e.g. after re-indexing)."""
    global _index, _chunks
    with _lock:
        _index  = None
        _chunks = []
    _ensure_loaded()
