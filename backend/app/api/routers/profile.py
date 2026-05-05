from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.api.dependencies import get_current_user
from app.core.supabase_client import supabase

router = APIRouter()

@router.get("/me")
async def get_my_profile(user: Any = Depends(get_current_user)):
    """
    Fetch the current user's profile and lawyer details if applicable.
    """
    client = supabase.get_admin_client()
    
    # Get profile data
    profile_res = client.table("profiles").select("*").eq("id", user.id).single().execute()
    if not profile_res.data:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    profile_data = profile_res.data
    
    # If lawyer, get lawyer specific data
    if profile_data.get("role") == "lawyer":
        lawyer_res = client.table("lawyers").select("*").eq("id", user.id).single().execute()
        if lawyer_res.data:
            profile_data["lawyer_details"] = lawyer_res.data
            
    return profile_data

@router.put("/me")
async def update_my_profile(
    profile_update: Dict[str, Any], 
    user: Any = Depends(get_current_user)
):
    """
    Update the current user's profile.
    """
    client = supabase.get_admin_client()
    
    # Separate profile and lawyer updates
    profile_fields = ["full_name", "phone_number", "avatar_url"]
    lawyer_fields = ["specialization", "bio", "location", "fee_per_consultation"]
    
    p_update = {k: v for k, v in profile_update.items() if k in profile_fields}
    l_update = {k: v for k, v in profile_update.items() if k in lawyer_fields}
    
    if p_update:
        client.table("profiles").update(p_update).eq("id", user.id).execute()
        
    if l_update:
        client.table("lawyers").update(l_update).eq("id", user.id).execute()
        
    return {"message": "Profile updated successfully"}
