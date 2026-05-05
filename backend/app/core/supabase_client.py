from supabase import create_client, Client
from app.core.config import settings

class SupabaseSingleton:
    """
    Singleton class to manage Supabase clients efficiently.
    Ensures we reuse the same Client connections across the app.
    """
    _instance: Client = None
    _admin_instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return cls._instance

    @classmethod
    def get_admin_client(cls) -> Client:
        if cls._admin_instance is None:
            cls._admin_instance = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        return cls._admin_instance

# Global singleton instance provider
supabase = SupabaseSingleton()
