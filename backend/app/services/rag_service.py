from typing import List, Dict, Any
import asyncio
from ai.core.qdrant_client import retrieve_chunks
from ai.services.groq_llm import generate_answer

class RagService:
    """
    A shared core service that bridges the dashboard to the AI (RAG) modules.
    Ensures consistent logic between the standalone AI API and the Dashboard UI.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RagService, cls).__new__(cls)
        return cls._instance

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Quick search without generation.
        Returns relevant chunks and metadata.
        """
        return retrieve_chunks(query, top_k=top_k)

    async def run_query(self, query: str) -> Dict[str, Any]:
        """
        Full generative QA pipeline.
        Returns: analysis, domain, cited_sections, cited_cases, cited_acts, confidence_score.
        """
        try:
            # 1. Retrieve context
            chunks = await asyncio.to_thread(retrieve_chunks, query)
            
            # 2. Generate answer
            llm_result = await asyncio.to_thread(generate_answer, query, chunks)
            
            # 3. Extract domain and citations from chunks for the dashboard UI
            domains = [c['metadata'].get('domain', 'general') for c in chunks]
            primary_domain = max(set(domains), key=domains.count) if domains else "general"
            
            sections = []
            acts = []
            for c in chunks:
                if c['metadata'].get('sections'):
                    sections.append(c['metadata']['sections'])
                if c['metadata'].get('acts'):
                    acts.append(c['metadata']['acts'])
            
            return {
                "analysis": llm_result["answer"],
                "domain": primary_domain,
                "cited_sections": list(set(sections)),
                "cited_acts": list(set(acts)),
                "cited_cases": [], # Add case extraction if available in metadata
                "confidence_score": chunks[0]["score"] if chunks else 0.0,
                "disclaimer": "This AI-generated information is for general guidance and does not constitute formal legal advice."
            }
        except Exception as e:
            print(f"RagService Error: {e}")
            return {
                "analysis": "We are currently experiencing high traffic. Please try again in a few moments.",
                "domain": "error",
                "cited_sections": [],
                "cited_acts": [],
                "cited_cases": [],
                "confidence_score": 0.0
            }

rag_service = RagService()
