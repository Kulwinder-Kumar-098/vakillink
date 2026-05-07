"""
pipeline/chunking.py
Split preprocessed legal documents into overlapping token-aware chunks.

Strategy:
  - Respects sentence boundaries (no mid-sentence splits)
  - Configurable token window and overlap
  - Propagates full metadata to every chunk
  - Assigns deterministic chunk IDs (hash-based)
"""
import hashlib
import re
from typing import List

from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Sentence splitter (lightweight, no NLTK dependency) ──────────────────────
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _approx_token_count(text: str) -> int:
    """Rough token count: ~4 chars per token (good enough for chunking)."""
    return max(1, len(text) // 4)


def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def _make_chunk_id(case_name: str, chunk_index: int, text_snippet: str) -> str:
    """Deterministic ID: sha1 of key fields → 12-char hex."""
    raw = f"{case_name}|{chunk_index}|{text_snippet[:50]}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


# ── Public API ────────────────────────────────────────────────────────────────

def chunk_record(
    record: dict,
    chunk_size:    int = None,
    chunk_overlap: int = None,
) -> List[dict]:
    """
    Split a single preprocessed record into chunks.
    Each chunk inherits the record's metadata.

    Args:
        record:        Preprocessed record dict (must have 'text').
        chunk_size:    Target token size per chunk (default from config).
        chunk_overlap: Overlap tokens between consecutive chunks.

    Returns:
        List of chunk dicts ready for embedding.
    """
    size    = chunk_size    or settings.CHUNK_SIZE_TOKENS
    overlap = chunk_overlap or settings.CHUNK_OVERLAP_TOKENS

    text = record.get("text", "").strip()
    if not text:
        return []

    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks:      List[dict] = []
    current:     List[str]  = []
    current_tok: int        = 0
    chunk_idx:   int        = 0

    # Sentence-aware sliding window
    for sent in sentences:
        sent_tok = _approx_token_count(sent)

        if current_tok + sent_tok > size and current:
            # Emit current window as a chunk
            chunk_text = " ".join(current)
            chunk_id   = _make_chunk_id(record["case_name"], chunk_idx, chunk_text)

            chunks.append({
                "chunk_id":    chunk_id,
                "chunk_index": chunk_idx,
                "text":        chunk_text,
                # metadata inherited
                "id":          record.get("id", ""),
                "case_name":   record["case_name"],
                "domain":      record["domain"],
                "subdomain":   record["subdomain"],
                "legal_issue": record["legal_issue"],
                "source":      record["source"],
                "acts":        record.get("acts", ""),
                "sections":    record.get("sections", ""),
                "year":        record.get("year", ""),
            })
            chunk_idx += 1

            # Keep overlap sentences at the tail
            overlap_tok = 0
            keep: List[str] = []
            for s in reversed(current):
                t = _approx_token_count(s)
                if overlap_tok + t > overlap:
                    break
                keep.insert(0, s)
                overlap_tok += t

            current     = keep
            current_tok = overlap_tok

        current.append(sent)
        current_tok += sent_tok

    # Flush remaining sentences
    if current:
        chunk_text = " ".join(current)
        chunk_id   = _make_chunk_id(record["case_name"], chunk_idx, chunk_text)
        chunks.append({
            "chunk_id":    chunk_id,
            "chunk_index": chunk_idx,
            "text":        chunk_text,
            "id":          record.get("id", ""),
            "case_name":   record["case_name"],
            "domain":      record["domain"],
            "subdomain":   record["subdomain"],
            "legal_issue": record["legal_issue"],
            "source":      record["source"],
            "acts":        record.get("acts", ""),
            "sections":    record.get("sections", ""),
            "year":        record.get("year", ""),
        })

    return chunks


def chunk_records(
    records: List[dict],
    chunk_size:    int = None,
    chunk_overlap: int = None,
) -> List[dict]:
    """
    Chunk all preprocessed records.
    Returns a flat list of chunk dicts.
    """
    all_chunks: List[dict] = []
    for rec in records:
        all_chunks.extend(chunk_record(rec, chunk_size, chunk_overlap))

    logger.info(
        f"Chunking: {len(records)} records → {len(all_chunks)} chunks "
        f"(avg {len(all_chunks)//max(1,len(records))} chunks/record)"
    )
    return all_chunks
