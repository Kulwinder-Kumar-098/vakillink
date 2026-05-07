"""
api/routes.py
FastAPI router for the Vakilink RAG pipeline.

Endpoints:
  POST /query          — full RAG: retrieve + generate
  POST /retrieve       — retrieval only (no LLM)
  GET  /domains        — list available legal domains
  GET  /health         — index health check
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from api.service import run_rag_pipeline, list_domains
from pipeline.indexing import index_exists
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query:          str           = Field(..., min_length=3, max_length=2000,
                                          description="The legal question to answer")
    domain:         Optional[str] = Field(None,  description="Filter by legal domain")
    top_k:          Optional[int] = Field(None,  ge=1, le=20,
                                          description="Number of chunks to retrieve")
    use_hybrid:     bool          = Field(True,  description="Use hybrid BM25+FAISS retrieval")
    use_reranker:   bool          = Field(False, description="Apply cross-encoder reranking")
    include_chunks: bool          = Field(False, description="Return raw chunks in response")


class SourceItem(BaseModel):
    index:       int
    case_name:   str
    domain:      str
    subdomain:   str
    legal_issue: str
    source:      str
    year:        int | str | None = None
    score:       float


class QueryResponse(BaseModel):
    answer:      str
    model:       str
    usage:       dict
    sources:     List[SourceItem]
    chunks_used: int
    chunks:      Optional[List[dict]] = None
    error:       Optional[str]        = None


class RetrieveRequest(BaseModel):
    query:         str           = Field(..., min_length=3, max_length=2000)
    domain:        Optional[str] = Field(None)
    top_k:         Optional[int] = Field(None, ge=1, le=20)
    use_hybrid:    bool          = Field(True)


class ChunkResult(BaseModel):
    chunk_id:    str
    score:       float
    text:        str
    case_name:   str
    domain:      str
    subdomain:   str
    legal_issue: str
    source:      str


class IndexHealth(BaseModel):
    index_ready:    bool
    message:        str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/query", response_model=QueryResponse, summary="Full RAG: retrieve + generate")
async def query_endpoint(request: QueryRequest):
    """
    Main RAG endpoint. Retrieves relevant legal chunks and generates
    an LLM answer with citations.
    """
    result = run_rag_pipeline(
        query=request.query,
        domain=request.domain,
        top_k=request.top_k,
        use_hybrid=request.use_hybrid,
        use_reranker=request.use_reranker,
        include_chunks=request.include_chunks,
    )

    if result["error"] and result["chunks_used"] == 0:
        # Hard failure (index missing, etc.) — return 503
        if "not found" in result["error"].lower() or "not loaded" in result["error"].lower():
            raise HTTPException(status_code=503, detail=result["error"])

    return QueryResponse(
        answer=result["answer"],
        model=result["model"],
        usage=result["usage"],
        sources=[SourceItem(**s) for s in result["sources"]],
        chunks_used=result["chunks_used"],
        chunks=result.get("chunks"),
        error=result.get("error"),
    )


@router.post("/retrieve", response_model=List[ChunkResult], summary="Retrieval only (no LLM)")
async def retrieve_endpoint(request: RetrieveRequest):
    """
    Retrieval-only endpoint. Returns raw chunks without LLM generation.
    Useful for debugging or building custom UIs.
    """
    from retriever.semantic_search import semantic_search
    from retriever.hybrid_search   import hybrid_search

    try:
        if request.use_hybrid:
            chunks = hybrid_search(
                query=request.query,
                top_k=request.top_k,
                domain_filter=request.domain,
            )
        else:
            chunks = semantic_search(
                query=request.query,
                top_k=request.top_k,
                domain_filter=request.domain,
            )

        return [
            ChunkResult(
                chunk_id=c.get("chunk_id", ""),
                score=c.get("score", 0.0),
                text=c.get("text", ""),
                case_name=c.get("case_name", ""),
                domain=c.get("domain", ""),
                subdomain=c.get("subdomain", ""),
                legal_issue=c.get("legal_issue", ""),
                source=c.get("source", ""),
            )
            for c in chunks
        ]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.error(f"Retrieval error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/domains", response_model=List[str], summary="List available legal domains")
async def domains_endpoint():
    """Returns the sorted list of unique legal domains available in the index."""
    try:
        return list_domains()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/health", response_model=IndexHealth, summary="Index health check")
async def rag_health():
    """Check if the FAISS index is available and loaded."""
    ready = index_exists()
    return IndexHealth(
        index_ready=ready,
        message=(
            "FAISS index is ready for queries."
            if ready else
            "FAISS index not found. Run 'python run_indexing.py' to build it."
        ),
    )
