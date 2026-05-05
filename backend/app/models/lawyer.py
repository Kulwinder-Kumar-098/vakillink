from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from .user import ProfileResponse

class LawyerBase(BaseModel):
    bar_council_id: str
    experience_years: int = Field(ge=0, description="Years of professional experience")
    bio: Optional[str] = None
    hourly_rate: Optional[float] = None
    languages: List[str] = []
    practice_areas: List[str] = []
    city: Optional[str] = None
    state: Optional[str] = None

class LawyerCreate(LawyerBase):
    pass # ID will be inherited from the created profile/auth user

class LawyerResponse(LawyerBase):
    id: UUID
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LawyerProfileResponse(BaseModel):
    """Aggregate model combining the user profile data and lawyer-specific data."""
    profile: ProfileResponse
    lawyer_details: LawyerResponse
    
    class Config:
        from_attributes = True

class LawyerAvailabilityBase(BaseModel):
    slot_start: datetime
    slot_end: datetime
    status: str = Field(default="available", pattern="^(available|booked|cancelled)$")

class LawyerAvailabilityResponse(LawyerAvailabilityBase):
    id: UUID
    lawyer_id: UUID
    
    class Config:
        from_attributes = True
