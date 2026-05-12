"""
utils/config.py
Central configuration for the Vakilink RAG pipeline.
Inherits from the shared app Settings so no duplicate .env values.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union

# ── Path helpers ──────────────────────────────────────────────────────────────
BACKEND_ROOT = Path(__file__).resolve().parent.parent

# Absolute paths for FAISS index artefacts (used by pipeline & retriever)
EMBEDDINGS_DIR  = BACKEND_ROOT / "data_pipeline" / "data" / "embeddings"
PROCESSED_DIR   = BACKEND_ROOT / "data_pipeline" / "data" / "processed_data"
FAISS_INDEX_PATH = EMBEDDINGS_DIR / "faiss_index.bin"
FAISS_META_PATH  = EMBEDDINGS_DIR / "faiss_metadata.json"


class PipelineSettings(BaseSettings):
    """All RAG-pipeline settings loaded from the project .env file."""

    # ── App ───────────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "VakilLink API"
    API_V1_STR:   str = "/api/v1"

    # ── Supabase (not used by pipeline but kept for env compatibility) ─────────
    SUPABASE_URL:              str = ""
    SUPABASE_KEY:              str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    JWT_SECRET:                str = "supersecretjwtkey"

    # ── Qdrant (cloud, used by main ai/core layer) ─────────────────────────────
    QDRANT_URL:        str = ""
    QDRANT_API_KEY:    str = ""
    QDRANT_COLLECTION: str = "legal_docs"

    # ── Groq LLM ─────────────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL:   str = "llama-3.3-70b-versatile"

    # ── Google AI (optional fallback) ─────────────────────────────────────────
    GOOGLE_API_KEY: str = ""

    # ── Embedding / FAISS ─────────────────────────────────────────────────────
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_MODEL:      str = "all-MiniLM-L6-v2"

    # ── RAG tuning ────────────────────────────────────────────────────────────
    TOP_K_RESULTS:        int   = 5
    SIMILARITY_THRESHOLD: float = 0.2
    CHUNK_SIZE_TOKENS:    int   = 400   # target tokens per chunk
    CHUNK_OVERLAP_TOKENS: int   = 50    # overlap between chunks

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:8501",   # Streamlit default
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = PipelineSettings()
