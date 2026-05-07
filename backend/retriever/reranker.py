"""
retriever/reranker.py
Cross-encoder reranker to refine retrieval results.

Uses a lightweight cross-encoder model (ms-marco-MiniLM-L-6-v2) to score
query-chunk pairs and re-sort the top candidates.

This module is OPTIONAL — if the cross-encoder model isn't installed or
fails to load, it falls back to the original ordering.
"""
from __future__ import annotations

import threading
from typing import List

from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker = None
_reranker_lock = threading.Lock()
_reranker_available = None   # None = not checked yet


def _get_reranker():
    """Load the cross-encoder once; return None if unavailable."""
    global _reranker, _reranker_available
    if _reranker_available is False:
        return None
    if _reranker is not None:
        return _reranker
    with _reranker_lock:
        if _reranker is not None:
            return _reranker
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder(_RERANKER_MODEL, max_length=512)
            _reranker_available = True
            logger.info(f"Reranker loaded: {_RERANKER_MODEL}")
        except Exception as exc:
            _reranker_available = False
            logger.warning(f"Reranker unavailable ({exc}) — skipping reranking.")
    return _reranker


def rerank(
    query:   str,
    results: List[dict],
    top_k:   int = None,
) -> List[dict]:
    """
    Rerank *results* using a cross-encoder and return top_k.

    If the cross-encoder is unavailable the original list is returned unchanged.

    Args:
        query:   The user query string.
        results: List of result dicts (must have 'text' key).
        top_k:   How many results to return after reranking.

    Returns:
        Re-sorted list of result dicts with added 'rerank_score' field.
    """
    k = top_k or settings.TOP_K_RESULTS

    if not results:
        return results

    model = _get_reranker()
    if model is None:
        return results[:k]

    try:
        pairs  = [(query, r["text"]) for r in results]
        scores = model.predict(pairs, show_progress_bar=False)

        for result, score in zip(results, scores):
            result["rerank_score"] = float(score)

        reranked = sorted(results, key=lambda x: x.get("rerank_score", 0), reverse=True)
        logger.info(f"Reranked {len(reranked)} candidates → returning top {k}")
        return reranked[:k]

    except Exception as exc:
        logger.warning(f"Reranking failed ({exc}) — returning original order.")
        return results[:k]
