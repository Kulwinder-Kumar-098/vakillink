"""
pipeline/preprocessing.py
Clean and normalise raw legal case records before chunking.

Operations:
  - Whitespace normalisation
  - Unicode normalisation (NFC)
  - Boilerplate removal (page headers, watermarks, etc.)
  - Field extraction and validation
  - Deduplication by case_id / id
"""
import re
import unicodedata
from typing import List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

# ── Regex patterns ────────────────────────────────────────────────────────────

_MULTI_NEWLINE   = re.compile(r"\n{3,}")
_MULTI_SPACE     = re.compile(r"[ \t]{2,}")
_PAGE_MARKER     = re.compile(r"\bpage\s+\d+\s+of\s+\d+\b", re.I)
_WATERMARK       = re.compile(r"(confidential|draft\s+copy|for\s+internal\s+use\s+only)", re.I)
_CONTROL_CHARS   = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


# ── Core helpers ──────────────────────────────────────────────────────────────

def _normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _clean_text(text: str) -> str:
    """Apply all text cleaning operations to a raw string."""
    if not text:
        return ""
    text = _normalize_unicode(text)
    text = _CONTROL_CHARS.sub(" ", text)        # strip control chars
    text = _PAGE_MARKER.sub(" ", text)          # remove page markers
    text = _WATERMARK.sub(" ", text)            # remove watermarks
    text = _MULTI_NEWLINE.sub("\n\n", text)     # collapse blank lines
    text = _MULTI_SPACE.sub(" ", text)          # collapse spaces
    return text.strip()


def _extract_field(record: dict, *keys: str, default: str = "") -> str:
    """Try multiple keys in order; return first non-empty string found."""
    for key in keys:
        val = record.get(key)
        if val and isinstance(val, str):
            v = val.strip()
            if v:
                return v
    return default


# ── Public API ────────────────────────────────────────────────────────────────

def preprocess_record(record: dict) -> Optional[dict]:
    """
    Clean a single raw record.
    Returns a normalised dict ready for chunking, or None if the record is
    unusable (missing text, too short, etc.).
    """
    # Extract main text — try multiple common field names
    raw_text = _extract_field(
        record,
        "text", "chunk_text", "body", "judgment_text",
        "case_text", "content", "full_text",
        default="",
    )
    text = _clean_text(raw_text)

    if len(text) < 50:          # too short to be useful
        return None

    # Extract metadata fields (with sensible fallbacks)
    case_name   = _extract_field(record, "case_name", "title", "case_title", default="Unknown Case")
    domain      = _extract_field(record, "domain", "category", "doc_type",   default="general")
    subdomain   = _extract_field(record, "subdomain", "sub_domain", "subtype", default="")
    legal_issue = _extract_field(record, "legal_issue", "issue", "legal_question", default="")
    source      = _extract_field(record, "source", "url", "citation", "reference", default="")
    doc_id      = _extract_field(record, "id", "case_id", "chunk_id", "doc_id", default="")
    acts        = _extract_field(record, "acts", "relevant_acts", "statutes",   default="")
    sections    = _extract_field(record, "sections", "relevant_sections",        default="")
    year        = str(_extract_field(record, "year", "decision_year", "date",    default=""))

    return {
        "id":          doc_id,
        "case_name":   _clean_text(case_name),
        "domain":      domain.lower().strip(),
        "subdomain":   subdomain.lower().strip(),
        "legal_issue": _clean_text(legal_issue),
        "source":      source.strip(),
        "acts":        acts,
        "sections":    sections,
        "year":        year,
        "text":        text,
    }


def preprocess_records(records: List[dict]) -> List[dict]:
    """
    Preprocess a list of raw records.
    Deduplicates by (case_name + text[:80]) fingerprint.
    """
    cleaned: List[dict]   = []
    seen:    set[str]     = set()
    skipped = 0

    for rec in records:
        result = preprocess_record(rec)
        if result is None:
            skipped += 1
            continue

        # Simple dedup fingerprint
        fp = f"{result['case_name']}|{result['text'][:80]}"
        if fp in seen:
            skipped += 1
            continue
        seen.add(fp)

        cleaned.append(result)

    logger.info(
        f"Preprocessing: {len(cleaned)} kept, {skipped} skipped "
        f"(total in: {len(records)})"
    )
    return cleaned
