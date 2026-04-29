import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

_supabase_client = None
_supabase_admin_client = None


def is_supabase_enabled():
    return USE_SUPABASE and SUPABASE_URL and SUPABASE_KEY


def get_supabase_client():
    global _supabase_client
    if _supabase_client is None and is_supabase_enabled():
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def get_supabase_admin():
    global _supabase_admin_client
    if _supabase_admin_client is None and is_supabase_enabled() and SUPABASE_SERVICE_KEY:
        from supabase import create_client
        _supabase_admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _supabase_admin_client
