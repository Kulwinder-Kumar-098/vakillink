from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.services.auth_service import AuthService
from app.models.user import UserCreate
from app.core.utils import generate_bar_council_id

router = APIRouter()
auth_service = AuthService()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(UserCreate):
    # Additional fields specific to our React Frontend forms
    bar_council_id: Optional[str] = None
    experience_years: Optional[int] = None

@router.post("/signup")
def signup(request: SignupRequest):
    """
    Register a new user. 
    If the role is 'lawyer' and no bar_council_id is provided, one will be generated.
    """
    user_data = request.model_dump()
    
    if user_data.get('role') == 'lawyer' and not user_data.get('bar_council_id'):
        # Automatically generate a Bar Council ID if not provided
        user_data['bar_council_id'] = generate_bar_council_id()
        
    return auth_service.signup_user(user_data)

@router.post("/login")
def login(request: LoginRequest):
    """
    Authenticate and retrieve a JWT token and user role.
    """
    return auth_service.login_user(request.email, request.password)
