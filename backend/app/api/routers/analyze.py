from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.rag_service import rag_service

router = APIRouter()

class AnalyzeRequest(BaseModel):
    category: str
    description: str
    dynamic_fields: Dict[str, Any]

class AnalyzeResponse(BaseModel):
    domain: str
    assessment: str
    urgency: str
    redirect_slug: str

def calculate_urgency(domain: str, text: str) -> str:
    text_lower = text.lower()
    high_keywords = ["arrest", "custody", "bail", "habeas corpus"]
    
    if domain in ["legal_criminal", "legal_constitutional"]:
        if any(kw in text_lower for kw in high_keywords):
            return "High"
        return "Medium"
    elif domain in ["legal_family", "legal_labour"]:
        return "Medium"
    elif domain == "legal_consumer":
        return "Low"
    return "Medium"  # Default

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_case(request: AnalyzeRequest):
    """
    Case Analyzer endpoint.
    Builds a query from structured inputs, hits the RAG pipeline, 
    and determines case urgency and appropriate lawyer domain routing.
    No auth required.
    """
    # 1. Construct the query
    dynamic_parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in request.dynamic_fields.items()]
    dynamic_str = "\n".join(dynamic_parts)
    
    constructed_query = (
        f"Category: {request.category}\n"
        f"Description: {request.description}\n"
        f"Additional Details:\n{dynamic_str}"
    )

    # 2. Run RAG Pipeline
    result = await rag_service.run_query(constructed_query)
    
    domain_identified = result.get("domain", "general")
    assessment = result.get("answer", "Error generating assessment.")

    # 3. Calculate Urgency
    urgency = calculate_urgency(domain_identified, constructed_query)

    return AnalyzeResponse(
        domain=domain_identified,
        assessment=assessment,
        urgency=urgency,
        redirect_slug=domain_identified  # The frontend uses this to route to /lawyers?domain=legal_criminal etc.
    )
