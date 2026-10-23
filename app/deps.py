"""FastAPI dependencies for database sessions and authentication."""
from typing import Annotated

from fastapi import Header

from app.security import verify_session_token


def get_current_session_id(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract session ID from Bearer token, or fallback to an anonymous session."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        verified = verify_session_token(token)
        if verified:
            return verified
    return "guest-session"
