"""
llm/prompt_builder.py
Build structured, citation-ready prompts for the Vakilink RAG pipeline.

Responsibilities:
  - Format retrieved chunks into a numbered context block
  - Inject domain context and query
  - Enforce strict legal-tone instructions
  - Keep total prompt within safe token limits (truncates chunks if needed)
"""
from __future__ import annotations

from typing import List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

# ── Approx token budget ───────────────────────────────────────────────────────
_APPROX_CHARS_PER_TOKEN = 4
_MAX_CONTEXT_CHARS      = 12_000   # safe for 16k-context models


# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are Vakilink, a Senior Legal AI Counsel specialising in Indian Law.

Your task is to provide a precise, well-reasoned legal analysis based STRICTLY \
on the context excerpts provided below. Do not use outside knowledge.

MANDATORY RULES:
1. CITE specific case names exactly as given (e.g., "As held in State v. Sharma…").
2. Reference relevant Acts, IPC/CrPC sections, or Constitutional Articles from the context.
3. If the context is insufficient to answer, clearly state:
   "Insufficient data in the current corpus to answer this question definitively."
4. Structure your response with:
   - **Summary** (2-3 sentences)
   - **Detailed Legal Analysis** (with inline citations like [Case 1], [Case 3])
   - **Conclusion**
5. Use formal legal language. Never speculate beyond the provided excerpts.
6. Format output in Markdown with bold headers.
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + " … [truncated]"


def _format_chunk(index: int, chunk: dict) -> str:
    """Format a single retrieval result into a labelled context block."""
    case_name   = chunk.get("case_name",   "Unknown Case")
    domain      = chunk.get("domain",      "General")
    subdomain   = chunk.get("subdomain",   "")
    legal_issue = chunk.get("legal_issue", "")
    source      = chunk.get("source",      "")
    acts        = chunk.get("acts",        "")
    sections    = chunk.get("sections",    "")
    year        = chunk.get("year",        "")
    text        = chunk.get("text",        "")
    score       = chunk.get("score",       0.0)

    domain_str = domain if not subdomain else f"{domain} › {subdomain}"
    meta_parts = [f"Domain: {domain_str}"]
    if year:        meta_parts.append(f"Year: {year}")
    if legal_issue: meta_parts.append(f"Issue: {legal_issue}")
    if acts:        meta_parts.append(f"Acts: {acts}")
    if sections:    meta_parts.append(f"Sections: {sections}")
    if source:      meta_parts.append(f"Source: {source}")

    return (
        f"--- [Case {index}] Similarity: {score:.1%} ---\n"
        f"Case: {case_name}\n"
        + " | ".join(meta_parts) + "\n\n"
        + text
        + "\n"
    )


# ── Public API ────────────────────────────────────────────────────────────────

def build_rag_prompt(
    query:         str,
    chunks:        List[dict],
    domain_hint:   Optional[str] = None,
    max_context:   int           = _MAX_CONTEXT_CHARS,
) -> tuple[str, str]:
    """
    Build a (system_prompt, user_message) pair for the LLM.

    Chunks are numbered and may be truncated to stay within token budget.

    Args:
        query:       The user's legal question.
        chunks:      Retrieval results (each with 'text', 'case_name', etc.)
        domain_hint: Optional domain string shown to the model for focus.
        max_context: Maximum character budget for all context blocks combined.

    Returns:
        (system_prompt: str, user_message: str)
    """
    if not chunks:
        user_message = (
            f"LEGAL QUERY: {query}\n\n"
            "CONTEXT: No relevant legal documents were retrieved from the corpus."
        )
        return SYSTEM_PROMPT, user_message

    # Build context blocks within budget
    context_blocks: List[str] = []
    budget = max_context

    for i, chunk in enumerate(chunks, start=1):
        block = _format_chunk(i, chunk)
        if len(block) > budget:
            block = _truncate(block, budget)
            context_blocks.append(block)
            logger.debug(f"Truncated chunk {i} to fit context budget.")
            break
        context_blocks.append(block)
        budget -= len(block)

    context_text = "\n".join(context_blocks)

    domain_line = f"LEGAL DOMAIN: {domain_hint}\n" if domain_hint else ""

    user_message = (
        f"{domain_line}"
        f"LEGAL QUERY: {query}\n\n"
        f"RETRIEVED CONTEXT ({len(context_blocks)} excerpt(s)):\n\n"
        f"{context_text}\n"
        f"INSTRUCTIONS:\n"
        f"- Answer using ONLY the context above.\n"
        f"- Cite case names using [Case N] notation.\n"
        f"- If context is insufficient, say so explicitly.\n"
        f"- Maintain a formal legal tone.\n"
    )

    logger.debug(
        f"Prompt built: {len(context_blocks)} chunks, "
        f"~{len(user_message)//_APPROX_CHARS_PER_TOKEN} tokens"
    )
    return SYSTEM_PROMPT, user_message


def format_sources(chunks: List[dict]) -> List[dict]:
    """
    Extract a clean source list for API response metadata.
    De-duplicates by case_name.
    """
    seen:    set[str]  = set()
    sources: List[dict] = []

    for i, c in enumerate(chunks, start=1):
        name = c.get("case_name", "Unknown")
        if name in seen:
            continue
        seen.add(name)
        sources.append({
            "index":       i,
            "case_name":   name,
            "domain":      c.get("domain",      ""),
            "subdomain":   c.get("subdomain",   ""),
            "legal_issue": c.get("legal_issue", ""),
            "source":      c.get("source",      ""),
            "year":        c.get("year",        ""),
            "score":       c.get("score",       0.0),
        })

    return sources
