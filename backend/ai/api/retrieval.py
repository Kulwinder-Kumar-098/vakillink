from fastapi import APIRouter, HTTPException
from ai.models.schemas import QueryRequest, QueryResponse, EmbedRequest, EmbedResponse, ChunkResult
from ai.core.qdrant_client import retrieve_chunks
from ai.services.groq_llm import generate_answer
from ai.core.embedder import embedder
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Full RAG pipeline: embed query → retrieve chunks → generate answer.
    
    This is the primary endpoint your Node.js backend will call.
    """
    try:
        # Step 1: Retrieve relevant chunks from Qdrant
        chunks = retrieve_chunks(
            query=request.query,
            top_k=request.top_k,
            doc_type_filter=request.doc_type,
        )

        # Step 2: Generate answer from Groq using the chunks as context
        result = generate_answer(query=request.query, chunks=chunks)

        # Step 3: Build response
        response = QueryResponse(
            answer=result["answer"],
            model=result["model"],
            usage=result["usage"],
            chunks_used=len(chunks),
            # Only include raw chunks if explicitly requested (saves bandwidth)
            chunks=[ChunkResult(**c) for c in chunks] if request.include_chunks else None,
        )

        return response

    except Exception as e:
        logger.error(f"RAG pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {str(e)}")


@router.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    """
    Embed a single text string. Useful for Node.js to precompute
    embeddings client-side or for debugging similarity searches.
    """
    try:
        vector = embedder.embed(request.text)
        return EmbedResponse(embedding=vector, dimensions=len(vector))
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrieve", response_model=list[ChunkResult])
async def retrieve(request: QueryRequest):
    """
    Retrieval-only endpoint — no LLM generation.
    Useful for: previewing what chunks a query finds, debugging, or
    when Node.js wants to handle answer generation differently.
    """
    try:
        chunks = retrieve_chunks(
            query=request.query,
            top_k=request.top_k,
            doc_type_filter=request.doc_type,
        )
        return [ChunkResult(**c) for c in chunks]
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
