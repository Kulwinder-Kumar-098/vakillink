from pydantic import BaseModel, Field
from typing import Optional


# ── Requests ─────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000, description="The legal question")
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="Override default chunk count")
    doc_type: Optional[str] = Field(default=None, description="Filter by doc type: statute, case_law, etc.")
    include_chunks: bool = Field(default=False, description="Whether to return raw chunks alongside the answer")


class EmbedRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


# ── Responses ─────────────────────────────────────────────────────────────────

class ChunkResult(BaseModel):
    id: str
    score: float
    text: str
    metadata: dict


class QueryResponse(BaseModel):
    answer: str
    model: str
    usage: dict
    chunks_used: int
    chunks: Optional[list[ChunkResult]] = None   # Only populated if include_chunks=True


class EmbedResponse(BaseModel):
    embedding: list[float]
    dimensions: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    qdrant_connected: bool
    version: str
