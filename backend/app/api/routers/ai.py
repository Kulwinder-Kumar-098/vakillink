from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import json
from app.api.dependencies import get_current_user
from app.services.rag_service import rag_service
from app.core.supabase_client import supabase
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    query: str

class LawyerRecommendation(BaseModel):
    id: str
    name: str
    specialization: str
    rating: float
    experience_years: int = 5
    available: str = "offline"
    avatar: Optional[str] = None

class QueryResponse(BaseModel):
    domain: str
    analysis: str
    cited_sections: List[str]
    cited_cases: List[str]
    cited_acts: List[str]
    disclaimer: str
    confidence_score: float
    recommended_lawyers: List[LawyerRecommendation]

@router.post("/query", response_model=QueryResponse)
@limiter.limit("5/minute")
async def ask_ai(request: Request, query_request: QueryRequest, user = Depends(get_current_user)):
    """
    Perform a full QA query against the RAG pipeline.
    Saves history to query_history.
    Fetches up to 3 recommended lawyers matching the identified legal domain.
    """
    # 1. Run RAG Pipeline
    result = await rag_service.run_query(query_request.query)
    
    analysis = result.get("analysis", result.get("answer", "Error processing request."))
    domain_identified = result.get("domain", "general")
    
    cited_sections = result.get("cited_sections", [])
    if isinstance(cited_sections, str):
        cited_sections = [cited_sections]
        
    cited_cases = result.get("cited_cases", [])
    if isinstance(cited_cases, str):
        cited_cases = [cited_cases]
        
    cited_acts = result.get("cited_acts", [])
    if isinstance(cited_acts, str):
        cited_acts = [cited_acts]
        
    disclaimer = result.get("disclaimer", "This AI-generated information is for general guidance and does not constitute formal legal advice. Please consult a qualified legal professional for your specific situation.")
    confidence_score = float(result.get("confidence_score", 0.0))

    # 2. Save to query_history (Fail-safe)
    try:
        client = supabase.get_admin_client()
        # Use a real user ID or fallback to None if it's the mock user
        db_user_id = user.id if user.id != '00000000-0000-0000-0000-000000000000' else None
        
        history_data = {
            "user_id": db_user_id,
            "query": query_request.query,
            "answer": result, 
            "domain": domain_identified
        }
        client.table("query_history").insert(history_data).execute()
    except Exception as e:
        print(f"[Database Error] Failed to save query_history: {e}")

    # 3. Fetch Lawyers (Fail-safe)
    recommended_lawyers = []
    if domain_identified not in ["general", "error", "unknown"]:
        try:
            # Note: We match on 'specialization' or 'domain' column depending on schema
            lawyers_res = client.table('lawyers') \
                .select('id, rating, domain, is_online, profiles(full_name, avatar_url)') \
                .eq('is_verified', True) \
                .or_(f"domain.eq.{domain_identified},specialization.eq.{domain_identified}") \
                .limit(3) \
                .execute()
                
            if lawyers_res.data:
                for lawyer in lawyers_res.data:
                    profile = lawyer.get("profiles", {})
                    recommended_lawyers.append(
                        LawyerRecommendation(
                            id=lawyer.get("id"),
                            name=profile.get("full_name", "Unknown Lawyer"),
                            specialization=lawyer.get("domain", domain_identified),
                            rating=lawyer.get("rating", 0.0) or 0.0,
                            experience_years=lawyer.get("experience_years", 5),
                            avatar=profile.get("avatar_url"),
                            available="online" if lawyer.get("is_online") else "offline"
                        )
                    )
            else:
                # If no lawyers found in DB, provide mock recommendations for the identified domain
                mock_names = {
                    "criminal": ["Adv. Rajesh Kumar", "Adv. Sanjay Singh"],
                    "family": ["Adv. Priya Sharma", "Adv. Meena Iyer"],
                    "constitutional": ["Adv. Vikram Singh", "Adv. Rahul Verma"],
                    "civil": ["Adv. Amit Shah", "Adv. Kavita Devi"]
                }
                names = mock_names.get(domain_identified, ["Adv. Suresh Raina", "Adv. Deepa Malik"])
                for i, name in enumerate(names):
                    recommended_lawyers.append(
                        LawyerRecommendation(
                            id=f"mock-{i}",
                            name=name,
                            specialization=domain_identified.capitalize() + " Law",
                            rating=4.8 + (i * 0.1),
                            available="online"
                        )
                    )
        except Exception as e:
            print(f"Failed to fetch recommended lawyers: {e}")

    return QueryResponse(
        domain=domain_identified,
        analysis=analysis,
        cited_sections=cited_sections,
        cited_cases=cited_cases,
        cited_acts=cited_acts,
        disclaimer=disclaimer,
        confidence_score=confidence_score,
        recommended_lawyers=recommended_lawyers
    )
