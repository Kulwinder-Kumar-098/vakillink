from groq import Groq
from ai.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client: Groq | None = None


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


SYSTEM_PROMPT = """You are a Senior Legal Counsel specializing in Indian Law. 
Your task is to provide a comprehensive, precise legal analysis based ON THE PROVIDED EXCERPTS.

STRICT RULES:
1. CITE specific case names, sections of the IPC/CrPC/Constitution, and Acts mentioned in the context.
2. USE ONLY the provided context chunks. If the context is insufficient, state that clearly.
3. FORMAT your response using Markdown with bold headers.
4. BE STRUCTURED: Start with a summary, then detailed analysis with citations, and end with a conclusion.
5. REFER to chunks by their index (e.g., [Chunk 1]) when citing information.
"""


def generate_answer(query: str, chunks: list[dict]) -> dict:
    """
    Send retrieved chunks + user query to Groq, return structured answer with legal citations.
    """
    if not chunks:
        return {
            "answer": "No relevant legal documents were found in the database for this specific query. Please try rephrasing or searching for a different legal topic.",
            "model": settings.GROQ_MODEL,
            "usage": {},
        }

    # Format chunks for the prompt with metadata for better citations
    context_blocks = []
    for i, c in enumerate(chunks):
        meta = c.get('metadata', {})
        block = (
            f"--- [Chunk {i+1}] ---\n"
            f"SOURCE: {meta.get('source', 'Unknown Document')}\n"
            f"DOMAIN: {meta.get('domain', 'General')}\n"
            f"LEGAL ISSUE: {meta.get('legal_issue', 'N/A')}\n"
            f"RELEVANT ACTS/SECTIONS: {meta.get('acts', 'N/A')} | {meta.get('sections', 'N/A')}\n"
            f"TEXT: {c['text']}\n"
        )
        context_blocks.append(block)
            
    context_text = "\n".join(context_blocks)

    user_message = f"USER QUERY: {query}\n\nLEGAL CONTEXT EXCERPTS:\n{context_text}"

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,   # Low temp = consistent legal answers
            max_tokens=1500,
        )

        answer = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

        logger.info(f"Groq answered successfully - tokens: {usage['total_tokens']}")
        return {"answer": answer, "model": settings.GROQ_MODEL, "usage": usage}

    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return {
            "answer": f"Error generating legal analysis: {str(e)}. Please check your Groq API key configuration.",
            "model": settings.GROQ_MODEL,
            "usage": {},
        }
