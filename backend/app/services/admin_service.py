from supabase import Client
from app.core.supabase_client import supabase
from fastapi import HTTPException
from typing import List, Dict, Any

class AdminService:
    def __init__(self):
        # Admin actions manage verification globally, so we use the admin client to bypass RLS
        self.admin_client: Client = supabase.get_admin_client()

    def get_pending_lawyers(self) -> List[Dict[str, Any]]:
        """
        Fetches all lawyers where is_verified is False.
        Joins with the profiles table to get their full name and contact info.
        """
        try:
            # Supabase automatically joins based on the foreign key relationship
            response = self.admin_client.table('lawyers') \
                .select('*, profiles(full_name, phone_number, email)') \
                .eq('is_verified', False) \
                .execute()
                
            return response.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch pending lawyers: {str(e)}")

    def approve_lawyer(self, lawyer_id: str) -> Dict[str, str]:
        """
        Sets is_verified to True for a given lawyer ID.
        """
        try:
            # Check if lawyer exists
            check = self.admin_client.table('lawyers').select('id').eq('id', lawyer_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Lawyer not found in the database.")

            # Update status
            response = self.admin_client.table('lawyers') \
                .update({'is_verified': True}) \
                .eq('id', lawyer_id) \
                .execute()
                
            return {"message": "Lawyer approved successfully.", "lawyer_id": lawyer_id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to approve lawyer: {str(e)}")

    def reject_lawyer(self, lawyer_id: str, reason: str = None) -> Dict[str, str]:
        """
        Rejects a lawyer application. 
        We delete the lawyer profile and demote the user back to a 'client' role.
        """
        try:
            # 1. Demote profile role to 'client'
            self.admin_client.table('profiles') \
                .update({'role': 'client'}) \
                .eq('id', lawyer_id) \
                .execute()
                
            # 2. Delete from lawyers table
            self.admin_client.table('lawyers') \
                .delete() \
                .eq('id', lawyer_id) \
                .execute()
                
            # TODO: In a production app, if `reason` is provided, trigger an email via Resend/SendGrid here
                
            return {"message": "Lawyer application rejected. User demoted to client.", "lawyer_id": lawyer_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to reject lawyer: {str(e)}")
