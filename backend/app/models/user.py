from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: str = Field(pattern="^(client|lawyer|admin)$", description="User role in the system")

class UserCreate(UserBase):
    password: str

class ProfileResponse(UserBase):
    id: UUID
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
