from fastapi import APIRouter, Depends
from typing import List, Any, Dict
from app.api.dependencies import get_current_user
from app.core.supabase_client import supabase

router = APIRouter()

@router.get("/")
async def get_archived_cases(user: Any = Depends(get_current_user)):
    """
    Get all saved/archived cases for the user.
    """
    client = supabase.get_admin_client()
    
    try:
        res = client.table("archived_cases").select("*").eq("user_id", user.id).execute()
        return res.data
    except Exception:
        # Fallback to mock
        return [
            {
                "id": 1,
                "title": "Maneka Gandhi vs Union of India",
                "citation": "1978 AIR 597",
                "domain": "CONSTITUTIONAL",
                "date": "2024-05-10"
            }
        ]

@router.post("/")
async def archive_case(
    case_data: Dict[str, Any], 
    user: Any = Depends(get_current_user)
):
    """
    Save a case to the user's archive.
    """
    client = supabase.get_admin_client()
    case_data["user_id"] = user.id
    
    res = client.table("archived_cases").insert(case_data).execute()
    return res.data

@router.delete("/{case_id}")
async def delete_archived_case(
    case_id: int, 
    user: Any = Depends(get_current_user)
):
    """
    Remove a case from the archive.
    """
    client = supabase.get_admin_client()
    client.table("archived_cases").delete().eq("id", case_id).eq("user_id", user.id).execute()
    return {"message": "Case removed from archive"}
