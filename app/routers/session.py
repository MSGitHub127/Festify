"""Anonymous session token generation endpoint."""
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.security import create_session_token

router = APIRouter(prefix="/api", tags=["Session"])


class SessionResponse(BaseModel):
    session_id: str
    token: str
    expires_in_minutes: int


@router.post("/session", response_model=SessionResponse)
def create_anonymous_session() -> SessionResponse:
    """Generate a privacy-preserving anonymous session ID and signed JWT token."""
    session_id = f"festify-{uuid.uuid4().hex[:12]}"
    token = create_session_token(session_id)
    return SessionResponse(session_id=session_id, token=token, expires_in_minutes=120)
