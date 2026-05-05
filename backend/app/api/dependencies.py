from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.core.supabase_client import supabase

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifies the Supabase JWT by making a call to Supabase's auth service.
    Returns the Supabase user object if the token is valid.
    """
    token = credentials.credentials
    
    # DEV BYPASS: Allow mock token for development testing
    if token == "mock_jwt_token":
        return type('MockUser', (), {'id': '00000000-0000-0000-0000-000000000000', 'email': 'test@example.com'})()

    client: Client = supabase.get_client()
    
    try:
        # Verifies token and fetches the user object
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token expired or invalid.")

def require_role(allowed_roles: list[str]):
    """
    Dependency generator to restrict route access based on user role.
    It fetches the user's role from the 'profiles' table using their UUID.
    """
    def role_checker(current_user = Depends(get_current_user)):
        client: Client = supabase.get_client()

        
        # Query the profile for the specific user's role
        response = client.table('profiles').select('role').eq('id', current_user.id).single().execute()
        
        if not response.data or 'role' not in response.data:
            raise HTTPException(status_code=403, detail="Profile not found or role missing.")
            
        user_role = response.data['role']
        if user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Action not allowed for role: {user_role}")
            
        return current_user
        
    return role_checker
