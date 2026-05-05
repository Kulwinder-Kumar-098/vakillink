from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import Optional, List, Dict, Any
from app.core.supabase_client import supabase
from app.api.dependencies import get_current_user, require_role

router = APIRouter()

@router.get("/")
def get_lawyers(
    domain: Optional[str] = Query(None, description="Filter by RAG domain / specialization"),
    location: Optional[str] = Query(None, description="Filter by location (ilike match)"),
    sort_by: Optional[str] = Query("rating", description="Sort by 'rating' or 'experience'"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search and filter verified lawyers. Public route.
    Returns a paginated array of lawyer cards.
    """
    client = supabase.get_client()
    query = client.table("lawyers").select("*", count="exact")

    if domain:
        query = query.eq("specialization", domain)
    if location:
        query = query.ilike("location", f"%{location}%")

    # Sorting
    if sort_by == "experience":
        query = query.order("experience_years", desc=True)
    else:
        # Default to rating
        query = query.order("rating", desc=True)

    # Pagination
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)

    try:
        response = query.execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for item in response.data:
        if "is_online" in item:
            item["available"] = "online" if item["is_online"] else "offline"
            
    return {
        "data": response.data,
        "total_count": response.count if hasattr(response, "count") else len(response.data),
        "page": page,
        "limit": limit
    }

@router.get("/{lawyer_id}")
def get_lawyer_profile(
    lawyer_id: str = Path(..., description="The ID of the lawyer")
):
    """
    Get the full lawyer profile including bio, areas_of_practice, latest 10 reviews,
    and availability schedule grouped by day.
    """
    client = supabase.get_client()
    
    try:
        # We fetch lawyer data, along with reviews and availability in a single query
        # We rely on Supabase PostgREST for the joins.
        response = client.table("lawyers").select(
            "*, lawyer_reviews(*), lawyer_availability(*)"
        ).eq("id", lawyer_id).execute()
        
        data = response.data
        if not data:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        
        lawyer_data = data[0]
        
        # Process reviews: sort by created_at descending and take top 10
        reviews = lawyer_data.get("lawyer_reviews", [])
        reviews.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        lawyer_data["lawyer_reviews"] = reviews[:10]
        
        # Process availability: group by day_of_week
        availability = lawyer_data.get("lawyer_availability", [])
        grouped_availability = {}
        for slot in availability:
            day = slot.get("day_of_week")
            if day not in grouped_availability:
                grouped_availability[day] = []
            grouped_availability[day].append({
                "id": slot.get("id"),
                "start_time": slot.get("start_time"),
                "end_time": slot.get("end_time")
            })
            
        lawyer_data["grouped_availability"] = grouped_availability
        
        # Remove the raw lawyer_availability array
        lawyer_data.pop("lawyer_availability", None)
        
        if "is_online" in lawyer_data:
            lawyer_data["available"] = "online" if lawyer_data["is_online"] else "offline"
            
        return lawyer_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me/profile")
def get_my_lawyer_profile(user = Depends(get_current_user)):
    """
    Get the logged-in lawyer's private profile.
    """
    # Assuming `get_current_user` logic exists in dependencies.
    client = supabase.get_client()
    response = client.table("lawyers").select("*").eq("id", user.id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return response.data[0]
