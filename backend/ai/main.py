from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from ai.api import retrieval, health
from ai.core.config import settings
from ai.core.embedder import embedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy models once at startup, not per-request."""
    logger.info("Loading embedding model...")
    embedder.load()
    logger.info(f"Model ready: {settings.EMBEDDING_MODEL}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Legal RAG API",
    description="FastAPI wrapper around the Legal RAG pipeline (embeddings + Qdrant + Groq)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(retrieval.router, prefix="/api/v1", tags=["retrieval"])
