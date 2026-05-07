"""
run_indexing.py
One-shot script to build the FAISS index from the existing .npy embeddings
and metadata JSON files already stored in data_pipeline/data/embeddings/.

This script is SMART:
  - If embeddings already exist as .npy files (from the old Nyaya-AI pipeline),
    it loads them directly — no re-embedding needed.
  - If new JSONL data directories exist, it processes those too.
  - Merges everything into one unified FAISS index.

Run once (or whenever the corpus changes):
    python run_indexing.py

Optional flags:
    --force        Rebuild even if index already exists
    --data-dir     Path to JSONL processed_data (default: data_pipeline/data/processed_data)
    --embed-dir    Path to .npy embeddings      (default: data_pipeline/data/embeddings)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import numpy as np

# ── Add backend root to sys.path so all imports work ─────────────────────────
BACKEND_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_ROOT))

from pipeline.indexing import (
    build_and_save,
    index_exists,
    FAISS_INDEX_PATH,
    FAISS_META_PATH,
)
from utils.logger import get_logger

logger = get_logger("run_indexing")


# ── Load existing .npy + metadata_*.json pairs ───────────────────────────────

def load_npy_embeddings(embed_dir: Path) -> tuple[np.ndarray | None, list[dict]]:
    """
    Load all embeddings_*.npy + metadata_*.json pairs from *embed_dir*.
    Returns (stacked_embeddings, flat_metadata_list).
    """
    npy_files = sorted(embed_dir.glob("embeddings_*.npy"))

    if not npy_files:
        logger.warning(f"No embeddings_*.npy files found in {embed_dir}")
        return None, []

    all_embs:  list[np.ndarray] = []
    all_meta:  list[dict]       = []
    processed_dir = embed_dir.parent / "processed_data"

    # Build a text lookup from all JSONL files (id → text)
    logger.info("Building text lookup from JSONL files …")
    id_to_text: dict[str, str] = {}
    for jf in (embed_dir.parent / "processed_data").rglob("*.jsonl"):
        try:
            with jf.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                        rec_id = rec.get("id") or rec.get("chunk_id") or ""
                        text   = rec.get("text") or rec.get("chunk_text") or ""
                        if rec_id:
                            id_to_text[rec_id] = text
                    except json.JSONDecodeError:
                        pass
        except Exception as exc:
            logger.warning(f"Could not read {jf}: {exc}")

    logger.info(f"Text lookup built: {len(id_to_text)} entries")

    for npy_path in npy_files:
        basename  = npy_path.stem.replace("embeddings_", "")
        meta_path = embed_dir / f"metadata_{basename}.json"

        if not meta_path.exists():
            logger.warning(f"Skipping {npy_path.name} — no matching metadata file.")
            continue

        try:
            embs = np.load(str(npy_path), allow_pickle=False).astype(np.float32)
            with meta_path.open("r", encoding="utf-8") as fh:
                meta = json.load(fh)

            if embs.shape[0] != len(meta):
                logger.warning(
                    f"{npy_path.name}: shape mismatch "
                    f"({embs.shape[0]} embs vs {len(meta)} meta) — skipping."
                )
                continue

            # Enrich metadata with text from JSONL lookup
            for rec in meta:
                if not rec.get("text"):
                    rec["text"] = id_to_text.get(rec.get("id", ""), "")
                # Ensure chunk_id exists
                if not rec.get("chunk_id"):
                    rec["chunk_id"] = rec.get("id", "")

            all_embs.append(embs)
            all_meta.extend(meta)
            logger.info(f"  ✓ {npy_path.name}: {embs.shape[0]} vectors")

        except Exception as exc:
            logger.error(f"Failed to load {npy_path.name}: {exc}")
            continue

    if not all_embs:
        return None, []

    stacked = np.vstack(all_embs)

    # L2-normalise (required for IndexFlatIP ≡ cosine similarity)
    norms   = np.linalg.norm(stacked, axis=1, keepdims=True)
    norms   = np.where(norms == 0, 1.0, norms)
    stacked = (stacked / norms).astype(np.float32)

    logger.info(
        f"Loaded {stacked.shape[0]} vectors (dim={stacked.shape[1]}) "
        f"from {len(all_embs)} .npy file(s)"
    )
    return stacked, all_meta


# ── Process fresh JSONL data ──────────────────────────────────────────────────

def process_jsonl_data(data_dir: Path) -> tuple[np.ndarray | None, list[dict]]:
    """
    Process any new JSONL records that don't have .npy counterparts.
    Uses the full pipeline: ingest → preprocess → chunk → embed.
    """
    jsonl_files = list(data_dir.rglob("*.jsonl"))
    if not jsonl_files:
        return None, []

    logger.info(f"Processing {len(jsonl_files)} JSONL file(s) from {data_dir} …")

    from pipeline.ingestion      import load_directory
    from pipeline.preprocessing  import preprocess_records
    from pipeline.chunking       import chunk_records
    from pipeline.embedding      import embed_chunks

    records = load_directory(data_dir)
    if not records:
        return None, []

    cleaned = preprocess_records(records)
    chunks  = chunk_records(cleaned)

    if not chunks:
        return None, []

    embeddings, chunks = embed_chunks(chunks)
    return embeddings, chunks


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build Vakilink FAISS index")
    parser.add_argument("--force",     action="store_true",
                        help="Rebuild index even if it already exists")
    parser.add_argument("--embed-dir", type=str,
                        default=str(BACKEND_ROOT / "data_pipeline" / "data" / "embeddings"),
                        help="Directory containing .npy embedding files")
    parser.add_argument("--data-dir",  type=str,
                        default=str(BACKEND_ROOT / "data_pipeline" / "data" / "processed_data"),
                        help="Directory containing JSONL processed data")
    parser.add_argument("--skip-npy",  action="store_true",
                        help="Skip loading pre-computed .npy files")
    parser.add_argument("--skip-jsonl", action="store_true",
                        help="Skip processing fresh JSONL data")
    args = parser.parse_args()

    embed_dir = Path(args.embed_dir)
    data_dir  = Path(args.data_dir)

    # ── Check if rebuild needed ───────────────────────────────────────────────
    if index_exists() and not args.force:
        logger.info(
            f"FAISS index already exists at {FAISS_INDEX_PATH}\n"
            "Use --force to rebuild."
        )
        return

    logger.info("=" * 60)
    logger.info("  Vakilink FAISS Index Builder")
    logger.info("=" * 60)

    all_embeddings: list[np.ndarray] = []
    all_chunks:     list[dict]       = []

    # ── Step 1: Load pre-computed .npy embeddings ─────────────────────────────
    if not args.skip_npy and embed_dir.exists():
        logger.info(f"\n[Step 1] Loading pre-computed embeddings from {embed_dir}")
        embs, meta = load_npy_embeddings(embed_dir)
        if embs is not None:
            all_embeddings.append(embs)
            all_chunks.extend(meta)
    else:
        logger.info("[Step 1] Skipped .npy loading.")

    # ── Step 2: Process fresh JSONL data ─────────────────────────────────────
    if not args.skip_jsonl and data_dir.exists():
        logger.info(f"\n[Step 2] Processing fresh JSONL data from {data_dir}")
        embs, chunks = process_jsonl_data(data_dir)
        if embs is not None:
            all_embeddings.append(embs)
            all_chunks.extend(chunks)
    else:
        logger.info("[Step 2] Skipped JSONL processing.")

    # ── Step 3: Merge and build FAISS index ───────────────────────────────────
    if not all_embeddings:
        logger.error(
            "\n❌ No embeddings found. "
            "Ensure .npy files exist in embed-dir or JSONL files in data-dir."
        )
        sys.exit(1)

    logger.info(f"\n[Step 3] Merging {len(all_embeddings)} embedding source(s) …")
    merged = np.vstack(all_embeddings)

    # Confirm normalisation
    norms  = np.linalg.norm(merged, axis=1, keepdims=True)
    norms  = np.where(norms == 0, 1.0, norms)
    merged = (merged / norms).astype(np.float32)

    logger.info(f"Final corpus: {merged.shape[0]} chunks, dim={merged.shape[1]}")
    logger.info(f"Unique domains: {sorted({c.get('domain','?') for c in all_chunks})}")

    logger.info("\n[Step 4] Building and saving FAISS index …")
    build_and_save(merged, all_chunks)

    logger.info("\n✅ Indexing complete!")
    logger.info(f"   Index  → {FAISS_INDEX_PATH}")
    logger.info(f"   Meta   → {FAISS_META_PATH}")
    logger.info(f"   Total  → {merged.shape[0]} chunks across {len(set(c.get('domain') for c in all_chunks))} domain(s)")
    logger.info("\nYou can now start the API server:")
    logger.info("   uvicorn main:app --reload --port 8000")
    logger.info("Or launch the Streamlit frontend:")
    logger.info("   streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
