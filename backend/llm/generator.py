"""
llm/generator.py
LLM answer generation for the Vakilink RAG pipeline.

Primary:  Groq (llama-3.3-70b-versatile) — fast, free tier available
Fallback: Google Gemini (if GOOGLE_API_KEY is configured)

Provides:
  - generate_answer(query, chunks)  → answer + sources + usage
  - Graceful error handling and timeout management
  - Token usage tracking
"""
from __future__ import annotations

import time
from typing import List, Optional

from llm.prompt_builder import build_rag_prompt, format_sources
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Groq client (lazy) ────────────────────────────────────────────────────────
_groq_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info("Groq client initialised.")
        except Exception as exc:
            logger.error(f"Failed to init Groq client: {exc}")
            raise
    return _groq_client


# ── Gemini fallback (lazy) ────────────────────────────────────────────────────
_gemini_model = None


def _get_gemini():
    global _gemini_model
    if _gemini_model is None:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Gemini model initialised (fallback).")
    return _gemini_model


# ── Core generators ───────────────────────────────────────────────────────────

def _generate_groq(system_prompt: str, user_message: str) -> dict:
    """Call Groq and return {answer, model, usage}."""
    client = _get_groq()
    t0 = time.time()

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_message},
        ],
        temperature=0.05,       # near-deterministic for legal accuracy
        max_tokens=2048,
        timeout=30,
    )

    elapsed = round(time.time() - t0, 2)
    answer  = response.choices[0].message.content
    usage   = {
        "prompt_tokens":     response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens":      response.usage.total_tokens,
        "latency_s":         elapsed,
    }

    logger.info(
        f"Groq generated answer: {usage['total_tokens']} tokens in {elapsed}s"
    )
    return {"answer": answer, "model": settings.GROQ_MODEL, "usage": usage}


def _generate_gemini(system_prompt: str, user_message: str) -> dict:
    """Call Gemini Flash and return {answer, model, usage}."""
    model   = _get_gemini()
    prompt  = f"{system_prompt}\n\n{user_message}"
    t0      = time.time()

    response = model.generate_content(prompt)
    elapsed  = round(time.time() - t0, 2)
    answer   = response.text

    usage = {
        "prompt_tokens":     getattr(response.usage_metadata, "prompt_token_count",      0),
        "completion_tokens": getattr(response.usage_metadata, "candidates_token_count",  0),
        "total_tokens":      getattr(response.usage_metadata, "total_token_count",       0),
        "latency_s":         elapsed,
    }

    logger.info(f"Gemini generated answer: {usage['total_tokens']} tokens in {elapsed}s")
    return {"answer": answer, "model": "gemini-1.5-flash", "usage": usage}


# ── Public API ────────────────────────────────────────────────────────────────

def generate_answer(
    query:       str,
    chunks:      List[dict],
    domain_hint: Optional[str] = None,
    use_hybrid:  bool          = True,
) -> dict:
    """
    Full RAG generation step.

    Args:
        query:       The user's legal question.
        chunks:      Retrieved and (optionally) reranked chunk dicts.
        domain_hint: Optional domain label passed to the prompt.
        use_hybrid:  Not used here directly; for caller-side branching.

    Returns:
        {
          "answer":  str,
          "model":   str,
          "usage":   dict,
          "sources": list[dict],
          "chunks_used": int,
        }
    """
    if not query.strip():
        return _empty_response("Query is empty.")

    # Build prompt
    system_prompt, user_message = build_rag_prompt(
        query=query,
        chunks=chunks,
        domain_hint=domain_hint,
    )

    # Try Groq first, fall back to Gemini if configured
    llm_result: Optional[dict] = None

    if settings.GROQ_API_KEY:
        try:
            llm_result = _generate_groq(system_prompt, user_message)
        except Exception as exc:
            logger.warning(f"Groq failed: {exc} — trying Gemini fallback.")

    if llm_result is None and settings.GOOGLE_API_KEY:
        try:
            llm_result = _generate_gemini(system_prompt, user_message)
        except Exception as exc:
            logger.error(f"Gemini fallback also failed: {exc}")

    if llm_result is None:
        return _empty_response(
            "LLM unavailable: both Groq and Gemini failed or are not configured. "
            "Please check your API keys in .env."
        )

    sources = format_sources(chunks)

    return {
        "answer":      llm_result["answer"],
        "model":       llm_result["model"],
        "usage":       llm_result["usage"],
        "sources":     sources,
        "chunks_used": len(chunks),
    }


def _empty_response(reason: str) -> dict:
    return {
        "answer":      reason,
        "model":       "none",
        "usage":       {},
        "sources":     [],
        "chunks_used": 0,
    }
