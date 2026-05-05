from supabase import Client
from app.core.supabase_client import supabase
from fastapi import HTTPException

class AuthService:
    def __init__(self):
        # We use standard client for auth, but admin client to bypass RLS when creating the initial profile records
        self.client: Client = supabase.get_client()
        self.admin_client: Client = supabase.get_admin_client()

    def signup_user(self, user_data: dict):
        try:
            # 1. Create the user in Supabase Auth
            auth_response = self.client.auth.sign_up({
                "email": user_data['email'],
                "password": user_data['password'],
                "options": {
                    "data": {
                        "full_name": user_data['full_name'],
                        "role": user_data['role']
                    }
                }
            })
            
            user = auth_response.user
            if not user:
                raise HTTPException(status_code=400, detail="Signup failed or email already exists.")
                
            # 2. Add to profiles table using admin client to bypass RLS
            profile_data = {
                "id": user.id,
                "role": user_data['role'],
                "full_name": user_data['full_name'],
                "phone_number": user_data.get('phone_number')
            }
            self.admin_client.table('profiles').insert(profile_data).execute()

            # 3. If lawyer, add to lawyers table
            if user_data['role'] == 'lawyer':
                lawyer_data = {
                    "id": user.id,
                    "bar_council_id": user_data.get('bar_council_id'),
                    "experience_years": user_data.get('experience_years', 0),
                }
                self.admin_client.table('lawyers').insert(lawyer_data).execute()

            return {"message": "User created successfully", "user_id": user.id, "role": user_data['role']}

        except Exception as e:
            # Catch Supabase Auth or DB errors (e.g. duplicate email)
            raise HTTPException(status_code=400, detail=str(e))

    def login_user(self, email: str, password: str):
        try:
            # 1. Sign in via Supabase Auth
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if not auth_response.session:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
            # 2. Fetch the user's role from the profiles table
            profile_response = self.client.table('profiles').select('role').eq('id', auth_response.user.id).single().execute()
            role = profile_response.data.get('role') if profile_response.data else 'client'
                
            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "token_type": "bearer",
                "role": role,
                "user_id": auth_response.user.id
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail="Authentication failed. Please check your credentials.")
