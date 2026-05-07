"""
pipeline/ingestion.py
Load raw JSONL legal case data from disk into memory.

Supports:
  - Single .jsonl files
  - Entire directories (recursive scan)
  - Automatic UTF-8 / latin-1 fallback
  - Skips malformed lines (logs them)
"""
import json
import os
from pathlib import Path
from typing import Iterator, List

from utils.logger import get_logger

logger = get_logger(__name__)


# ── Public API ────────────────────────────────────────────────────────────────

def load_jsonl(path: str | Path) -> List[dict]:
    """
    Load all records from a single JSONL file.
    Returns a list of dicts.  Skips blank/broken lines.
    """
    path = Path(path)
    records: List[dict] = []
    bad = 0

    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with path.open("r", encoding=enc) as fh:
                for lineno, raw in enumerate(fh, start=1):
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        records.append(json.loads(raw))
                    except json.JSONDecodeError:
                        bad += 1
                        logger.debug(f"Skipping malformed line {lineno} in {path.name}")
            break   # success — stop trying encodings
        except UnicodeDecodeError:
            records.clear()
            bad = 0
            continue

    if bad:
        logger.warning(f"{path.name}: skipped {bad} malformed line(s)")

    logger.info(f"Loaded {len(records)} records from {path.name}")
    return records


def load_directory(directory: str | Path, pattern: str = "**/*.jsonl") -> List[dict]:
    """
    Recursively load all JSONL files under *directory*.
    Returns a single flat list of all records.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")

    all_records: List[dict] = []
    files = sorted(directory.glob(pattern))

    if not files:
        logger.warning(f"No JSONL files matched '{pattern}' in {directory}")
        return all_records

    for fp in files:
        all_records.extend(load_jsonl(fp))

    logger.info(
        f"Ingestion complete: {len(all_records)} total records "
        f"from {len(files)} file(s) in {directory}"
    )
    return all_records


def stream_jsonl(path: str | Path) -> Iterator[dict]:
    """
    Memory-efficient generator — yields one record at a time.
    Use this for very large files.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                yield json.loads(raw)
            except json.JSONDecodeError:
                logger.debug(f"Skipping malformed line in {path.name}")
