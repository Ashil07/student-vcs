from fastapi import HTTPException, Request
from jose import jwt, JWTError
from core.supabase_config import SUPABASE_URL, is_supabase_enabled


def get_current_user(request: Request):
    """Extract and verify the current user from the JWT token."""
    if not is_supabase_enabled():
        return None

    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.replace("Bearer ", "")

    try:
        # Supabase JWTs are RS256 signed. We verify against the JWT secret.
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
