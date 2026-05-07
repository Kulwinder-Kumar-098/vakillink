"""
api/service.py
Core RAG orchestration service — decoupled from FastAPI so it can be
called by both the REST API and the Streamlit app.

Pipeline per query:
  1. Validate input
  2. Retrieve chunks (FAISS semantic OR hybrid)
  3. Optionally rerank
  4. Generate LLM answer
  5. Return structured response dict
"""
from __future__ import annotations

from typing import Optional

from retriever.semantic_search import semantic_search, get_available_domains
from retriever.hybrid_search   import hybrid_search
from retriever.reranker        import rerank
from llm.generator             import generate_answer
from utils.config              import settings
from utils.logger              import get_logger

logger = get_logger(__name__)


# ── Exported helpers ──────────────────────────────────────────────────────────

def list_domains() -> list[str]:
    """Return all unique legal domains in the loaded index."""
    try:
        return get_available_domains()
    except Exception:
        return []


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_rag_pipeline(
    query:           str,
    domain:          Optional[str] = None,
    top_k:           int           = None,
    use_hybrid:      bool          = True,
    use_reranker:    bool          = False,
    include_chunks:  bool          = False,
) -> dict:
    """
    End-to-end RAG pipeline.

    Args:
        query:          User's legal question (must be non-empty).
        domain:         Optional domain filter (e.g. 'criminal', 'family').
        top_k:          Number of final results to use for generation.
        use_hybrid:     If True, use BM25+FAISS hybrid retrieval.
        use_reranker:   If True, apply cross-encoder reranking.
        include_chunks: If True, attach raw chunk dicts to the response.

    Returns:
        {
          "answer":       str,
          "model":        str,
          "usage":        dict,
          "sources":      list[dict],
          "chunks_used":  int,
          "chunks":       list[dict] | None,
          "error":        str | None,
        }
    """
    # ── 0. Validate ───────────────────────────────────────────────────────────
    query = query.strip()
    if not query:
        return _error_response("Query cannot be empty.")
    if len(query) < 3:
        return _error_response("Query is too short. Please provide more detail.")

    k = top_k or settings.TOP_K_RESULTS

    try:
        # ── 1. Retrieval ──────────────────────────────────────────────────────
        if use_hybrid:
            chunks = hybrid_search(query, top_k=k * 2, domain_filter=domain)
        else:
            chunks = semantic_search(query, top_k=k * 2, domain_filter=domain)

        if not chunks:
            return _error_response(
                "No relevant legal documents were found for this query. "
                "Try different keywords or remove the domain filter.",
                answer="Insufficient data in the current corpus to answer this question. "
                       "Please try rephrasing your query.",
            )

        # ── 2. Optional reranking ─────────────────────────────────────────────
        if use_reranker:
            chunks = rerank(query, chunks, top_k=k)
        else:
            chunks = chunks[:k]

        # ── 3. LLM Generation ─────────────────────────────────────────────────
        result = generate_answer(
            query=query,
            chunks=chunks,
            domain_hint=domain,
        )

        # ── 4. Build response ─────────────────────────────────────────────────
        return {
            "answer":      result["answer"],
            "model":       result["model"],
            "usage":       result["usage"],
            "sources":     result["sources"],
            "chunks_used": result["chunks_used"],
            "chunks":      chunks if include_chunks else None,
            "error":       None,
        }

    except RuntimeError as exc:
        # Index not loaded, etc.
        logger.error(f"Pipeline runtime error: {exc}")
        return _error_response(str(exc))

    except Exception as exc:
        logger.error(f"Unexpected pipeline error: {exc}", exc_info=True)
        return _error_response(
            f"An internal error occurred: {type(exc).__name__}. "
            "Please check server logs for details."
        )


def _error_response(reason: str, answer: str = None) -> dict:
    return {
        "answer":      answer or reason,
        "model":       "none",
        "usage":       {},
        "sources":     [],
        "chunks_used": 0,
        "chunks":      None,
        "error":       reason,
    }
