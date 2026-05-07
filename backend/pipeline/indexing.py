"""
pipeline/indexing.py
Build and persist a FAISS index from chunk embeddings.

Strategy:
  - IndexFlatIP  (exact inner-product search, equiv. cosine on L2-normed vecs)
  - Metadata saved to a parallel JSON file
  - Supports incremental re-indexing (merge new chunks into existing index)
  - Provides save / load helpers used by the retriever
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

import faiss
import numpy as np

from utils.config import settings, FAISS_INDEX_PATH, FAISS_META_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


# ── Build ─────────────────────────────────────────────────────────────────────

def build_index(
    embeddings: np.ndarray,
    chunks: List[dict],
) -> tuple[faiss.IndexFlatIP, List[dict]]:
    """
    Build a FAISS IndexFlatIP from L2-normalised embeddings.

    Args:
        embeddings: Float32 array of shape (N, dim).
        chunks:     Parallel list of chunk metadata dicts (len == N).

    Returns:
        (faiss_index, chunks)
    """
    if len(embeddings) != len(chunks):
        raise ValueError(
            f"Mismatch: {len(embeddings)} embeddings vs {len(chunks)} chunks"
        )

    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    logger.info(f"FAISS index built: {index.ntotal} vectors, dim={dim}")
    return index, chunks


def save_index(
    index:      faiss.IndexFlatIP,
    chunks:     List[dict],
    index_path: Path = FAISS_INDEX_PATH,
    meta_path:  Path = FAISS_META_PATH,
) -> None:
    """Persist the FAISS index and metadata to disk."""
    index_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_path))
    logger.info(f"FAISS index saved → {index_path}")

    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(chunks, fh, ensure_ascii=False, indent=2)
    logger.info(f"Metadata saved   → {meta_path}  ({len(chunks)} records)")


def load_index(
    index_path: Path = FAISS_INDEX_PATH,
    meta_path:  Path = FAISS_META_PATH,
) -> tuple[faiss.IndexFlatIP, List[dict]]:
    """
    Load a previously saved FAISS index and metadata.
    Raises FileNotFoundError if either file is missing.
    """
    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index not found: {index_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {meta_path}")

    index = faiss.read_index(str(index_path))
    logger.info(f"FAISS index loaded: {index.ntotal} vectors from {index_path}")

    with meta_path.open("r", encoding="utf-8") as fh:
        chunks = json.load(fh)
    logger.info(f"Metadata loaded: {len(chunks)} chunks")

    if index.ntotal != len(chunks):
        raise RuntimeError(
            f"Index/metadata mismatch: {index.ntotal} vectors vs {len(chunks)} metadata rows"
        )

    return index, chunks


def index_exists(
    index_path: Path = FAISS_INDEX_PATH,
    meta_path:  Path = FAISS_META_PATH,
) -> bool:
    """Return True only if both the FAISS index and metadata files exist."""
    return index_path.exists() and meta_path.exists()


# ── Convenience: full pipeline run ────────────────────────────────────────────

def build_and_save(embeddings: np.ndarray, chunks: List[dict]) -> None:
    """One-shot: build index + save to the paths defined in config."""
    index, chunks = build_index(embeddings, chunks)
    save_index(index, chunks)
