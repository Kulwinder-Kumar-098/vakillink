from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from app.api.dependencies import get_current_user
from app.core.supabase_client import supabase
from pydantic import BaseModel

router = APIRouter()

class Consultation(BaseModel):
    client_name: str
    type: str
    date: str
    time: str
    status: str
    case_domain: str
    fee: str

@router.get("/", response_model=List[Dict[str, Any]])
async def get_my_consultations(user: Any = Depends(get_current_user)):
    """
    Fetch consultations for the current user.
    If lawyer, shows appointments with clients.
    If client, shows appointments with lawyers.
    """
    client = supabase.get_admin_client()
    
    # This is a simplified version using a mock or a generic table
    # In a real app, you'd have a 'consultations' table
    try:
        res = client.table("consultations").select("*").or_(f"lawyer_id.eq.{user.id},client_id.eq.{user.id}").execute()
        return res.data
    except Exception:
        # Fallback to mock data if table doesn't exist yet
        return [
            {
                "id": 1,
                "client_name": "Rahul Deshmukh",
                "type": "Video Call",
                "date": "2024-05-15",
                "time": "10:30 AM",
                "status": "Upcoming",
                "case_domain": "Property Dispute",
                "fee": "₹2,500"
            }
        ]

@router.post("/")
async def create_consultation(
    consultation: Dict[str, Any], 
    user: Any = Depends(get_current_user)
):
    """
    Book a new consultation.
    """
    client = supabase.get_admin_client()
    consultation["client_id"] = user.id
    
    res = client.table("consultations").insert(consultation).execute()
    return res.data
