"""
pipeline/embedding.py
Compute sentence-transformer embeddings for text chunks.

Features:
  - Batch processing with configurable batch size
  - Progress logging
  - Returns numpy arrays (float32)
  - Normalises vectors for cosine similarity via FAISS IndexFlatIP
"""
from __future__ import annotations

import numpy as np
from typing import List

from sentence_transformers import SentenceTransformer

from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Singleton model ───────────────────────────────────────────────────────────
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Load the embedding model once and cache it in the module."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        logger.info("Embedding model ready.")
    return _model


# ── Public API ────────────────────────────────────────────────────────────────

def embed_texts(
    texts: List[str],
    batch_size: int = 64,
    normalize: bool = True,
    show_progress: bool = True,
) -> np.ndarray:
    """
    Embed a list of strings.

    Args:
        texts:         Strings to embed.
        batch_size:    Number of texts per GPU/CPU batch.
        normalize:     L2-normalise so dot product == cosine similarity.
        show_progress: Print a tqdm progress bar (useful for large corpora).

    Returns:
        Float32 numpy array of shape (len(texts), embedding_dim).
    """
    model = get_model()

    logger.info(f"Embedding {len(texts)} texts (batch_size={batch_size}) …")

    embeddings: np.ndarray = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=normalize,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
    )

    logger.info(f"Embedding complete: shape={embeddings.shape}, dtype={embeddings.dtype}")
    return embeddings.astype(np.float32)


def embed_chunks(
    chunks: List[dict],
    batch_size: int = 64,
) -> tuple[np.ndarray, List[dict]]:
    """
    Embed the 'text' field of each chunk dict.

    Returns:
        (embeddings_array, chunks)  — parallel arrays; index i corresponds.
    """
    if not chunks:
        raise ValueError("chunk list is empty — nothing to embed")

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts, batch_size=batch_size)
    return embeddings, chunks


def embed_query(query: str) -> np.ndarray:
    """
    Embed a single query string for retrieval.
    Returns shape (1, dim) float32 array, L2-normalised.
    """
    return embed_texts([query], show_progress=False)
