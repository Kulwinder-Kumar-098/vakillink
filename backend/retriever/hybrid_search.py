"""
retriever/hybrid_search.py
Hybrid retrieval: combines FAISS semantic scores with BM25 keyword scores.

Algorithm:
  1. Dense retrieval (FAISS) → top_k * 4 candidates
  2. BM25 sparse retrieval over candidate texts
  3. Reciprocal Rank Fusion (RRF) to merge ranked lists
  4. Return top_k fused results

BM25 is computed on-the-fly over the candidate pool (fast, no index needed).
RRF constant k=60 (standard default from the original paper).
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import List, Optional

from retriever.semantic_search import semantic_search
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_RRF_K = 60  # Reciprocal Rank Fusion constant


# ── BM25 helpers ──────────────────────────────────────────────────────────────

def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


def _bm25_scores(
    query_tokens: List[str],
    docs: List[str],
    k1: float = 1.5,
    b:  float = 0.75,
) -> List[float]:
    """
    Compute BM25 score for each doc against query_tokens.
    """
    N   = len(docs)
    avgdl = sum(len(_tokenize(d)) for d in docs) / max(1, N)

    # IDF
    df: dict[str, int] = defaultdict(int)
    for doc in docs:
        unique = set(_tokenize(doc))
        for t in query_tokens:
            if t in unique:
                df[t] += 1

    idf: dict[str, float] = {}
    for t in query_tokens:
        n = df[t]
        idf[t] = math.log((N - n + 0.5) / (n + 0.5) + 1)

    # TF-adjusted scoring
    scores: List[float] = []
    for doc in docs:
        tokens  = _tokenize(doc)
        tf_cnt  = Counter(tokens)
        dl      = len(tokens)
        score   = 0.0
        for t in query_tokens:
            tf = tf_cnt.get(t, 0)
            score += idf[t] * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
        scores.append(score)

    return scores


def _rrf(rankings: List[List[str]], k: int = _RRF_K) -> List[tuple[str, float]]:
    """
    Reciprocal Rank Fusion over multiple ranked lists of IDs.
    Returns list of (id, rrf_score) sorted descending.
    """
    rrf_scores: dict[str, float] = defaultdict(float)
    for ranked in rankings:
        for rank, doc_id in enumerate(ranked, start=1):
            rrf_scores[doc_id] += 1.0 / (k + rank)
    return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)


# ── Public API ────────────────────────────────────────────────────────────────

def hybrid_search(
    query:         str,
    top_k:         int           = None,
    domain_filter: Optional[str] = None,
) -> List[dict]:
    """
    Hybrid semantic + BM25 search with RRF fusion.

    Returns top_k result dicts sorted by fused RRF score.
    """
    k = top_k or settings.TOP_K_RESULTS

    # Step 1: Dense retrieval — get a large candidate pool
    candidates = semantic_search(
        query,
        top_k=k * 4,
        domain_filter=domain_filter,
        score_threshold=0.0,    # collect all scores — RRF will re-rank
    )

    if not candidates:
        return []

    if len(candidates) <= k:
        return candidates[:k]

    # Step 2: BM25 over candidate texts
    texts  = [c["text"] for c in candidates]
    q_tok  = _tokenize(query)
    bm25   = _bm25_scores(q_tok, texts)

    # Step 3: Build ranked lists (by ID)
    id_map       = {c["chunk_id"]: c for c in candidates}
    dense_ranked = [c["chunk_id"] for c in candidates]   # already sorted by score
    bm25_ranked  = [
        candidates[i]["chunk_id"]
        for i in sorted(range(len(bm25)), key=lambda j: bm25[j], reverse=True)
    ]

    # Step 4: RRF fusion
    fused = _rrf([dense_ranked, bm25_ranked])

    results = []
    for doc_id, rrf_score in fused[:k]:
        chunk = id_map[doc_id].copy()
        chunk["rrf_score"] = round(rrf_score, 6)
        results.append(chunk)

    logger.info(
        f"Hybrid search: '{query[:60]}' → {len(results)} results "
        f"(pool={len(candidates)}, domain={domain_filter or 'all'})"
    )
    return results
