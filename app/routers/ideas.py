"""GenAI creative personalization, grounded Q&A, and client dossier export."""
from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.llm.provider import get_llm_provider
from app.models import CreativeIdeas, EventRecord
from app.security import decrypt_data, sanitize_prompt_input

router = APIRouter(prefix="/api", tags=["Ideas & Consultation"])


class AskQuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, description="Planner or client question")


class AskQuestionResponse(BaseModel):
    question: str
    answer: str
    grounded: bool


class StatelessIdeaRequest(BaseModel):
    event_type: str = Field(default="wedding")
    vibe_theme: str | None = Field(default=None)


@router.post("/ideas/generate", response_model=CreativeIdeas)
def generate_stateless_ideas(request: StatelessIdeaRequest) -> CreativeIdeas:
    """Generate cohesive creative themes, dietary-inclusive menus, and speech drafts."""
    provider = get_llm_provider()
    return provider.generate_ideas(request.event_type, request.vibe_theme)


@router.post("/events/{event_id}/ask", response_model=AskQuestionResponse)
def ask_event_question(
    event_id: str,
    request: AskQuestionRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AskQuestionResponse:
    """Answer questions grounded strictly in the generated event plan."""
    record = db.get(EventRecord, event_id)
    if not record or not record.encrypted_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    decrypted = json.loads(decrypt_data(record.encrypted_details))
    context = decrypted.get("dossier", "")

    provider = get_llm_provider()
    sanitized_q = sanitize_prompt_input(request.question)
    answer = provider.answer_event_query(sanitized_q, context)

    return AskQuestionResponse(
        question=sanitized_q,
        answer=answer,
        grounded=True,
    )


@router.get("/events/{event_id}/dossier")
def export_event_dossier(
    event_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Export the formatted Markdown Client & Vendor Dossier."""
    record = db.get(EventRecord, event_id)
    if not record or not record.encrypted_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    decrypted = json.loads(decrypt_data(record.encrypted_details))
    dossier_text = decrypted.get("dossier", "# Event Dossier Not Found")

    return Response(
        content=dossier_text,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="festify_{event_id}_dossier.md"'},
    )
