"""Event creation, retrieval, and orchestration endpoints."""
from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_session_id
from app.models import EventCreateRequest, EventRecord, FullEventPlanResponse
from app.planner.budget_engine import generate_budget_breakdown
from app.planner.dossier import compile_event_dossier
from app.planner.idea_engine import generate_creative_ideas
from app.planner.permit_rules import evaluate_statutory_permits
from app.planner.timeline_engine import generate_timeline_plan
from app.planner.vendor_rubric import get_vendor_checklists
from app.security import decrypt_data, encrypt_data, redact_pii

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.post("", response_model=FullEventPlanResponse, status_code=status.HTTP_201_CREATED)
def create_event_plan(
    request: EventCreateRequest,
    session_id: Annotated[str, Depends(get_current_session_id)],
    db: Annotated[Session, Depends(get_db)],
) -> FullEventPlanResponse:
    """Create a comprehensive event plan: budget, timeline, vendor rubrics, ideas, and permits."""
    # Step 1: PII Redaction
    title_sanitized = redact_pii(request.title).sanitized_text
    vibe_sanitized = redact_pii(request.vibe_theme).sanitized_text
    notes_sanitized = redact_pii(request.special_requirements or "").sanitized_text

    # Step 2: Domain Intelligence Generation
    budget_plan = generate_budget_breakdown(request.event_type.value, request.total_budget, request.guest_count)
    timeline_plan = generate_timeline_plan(request.event_type.value)
    vendor_rubrics = get_vendor_checklists(request.event_type.value)
    creative_ideas = generate_creative_ideas(request.event_type.value, vibe_sanitized)
    statutory_permits = evaluate_statutory_permits(request.event_type.value, request.guest_count, request.location)

    # Step 3: Compile Markdown Dossier
    dossier_md = compile_event_dossier(
        title=title_sanitized,
        event_type=request.event_type.value,
        guest_count=request.guest_count,
        total_budget=request.total_budget,
        vibe_theme=vibe_sanitized,
        budget=budget_plan,
        timeline=timeline_plan,
        vendor_rubric=vendor_rubrics,
        creative_ideas=creative_ideas,
        permits=statutory_permits,
    )

    # Step 4: Encrypt and Persist
    serialized_plan = {
        "budget": budget_plan.model_dump(),
        "timeline": timeline_plan.model_dump(),
        "vendor_rubric": [v.model_dump() for v in vendor_rubrics],
        "creative_ideas": creative_ideas.model_dump(),
        "statutory_permits": statutory_permits.model_dump(),
        "dossier": dossier_md,
        "special_notes": notes_sanitized,
    }
    encrypted_payload = encrypt_data(json.dumps(serialized_plan))

    event_record = EventRecord(
        session_id=session_id,
        event_type=request.event_type.value,
        title=title_sanitized,
        event_date=request.event_date,
        location=request.location,
        guest_count=request.guest_count,
        total_budget=request.total_budget,
        vibe_theme=vibe_sanitized,
        encrypted_details=encrypted_payload,
    )
    db.add(event_record)
    db.commit()
    db.refresh(event_record)

    return FullEventPlanResponse(
        event_id=event_record.id,
        event_type=event_record.event_type,
        title=event_record.title,
        guest_count=event_record.guest_count,
        total_budget=event_record.total_budget,
        vibe_theme=event_record.vibe_theme,
        budget=budget_plan,
        timeline=timeline_plan,
        vendor_rubric=vendor_rubrics,
        creative_ideas=creative_ideas,
        statutory_permits=statutory_permits,
        client_dossier_markdown=dossier_md,
    )


@router.get("/{event_id}", response_model=FullEventPlanResponse)
def get_event_plan(
    event_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> FullEventPlanResponse:
    """Retrieve an existing event plan by ID."""
    record = db.get(EventRecord, event_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event plan not found.")

    if not record.encrypted_details:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Corrupted event record.")

    decrypted_json = decrypt_data(record.encrypted_details)
    plan_dict = json.loads(decrypted_json)

    return FullEventPlanResponse(
        event_id=record.id,
        event_type=record.event_type,
        title=record.title,
        guest_count=record.guest_count,
        total_budget=record.total_budget,
        vibe_theme=record.vibe_theme,
        budget=plan_dict["budget"],
        timeline=plan_dict["timeline"],
        vendor_rubric=plan_dict["vendor_rubric"],
        creative_ideas=plan_dict["creative_ideas"],
        statutory_permits=plan_dict["statutory_permits"],
        client_dossier_markdown=plan_dict["dossier"],
    )


@router.get("", response_model=list[dict])
def list_session_events(
    session_id: Annotated[str, Depends(get_current_session_id)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    """List summary cards for all events in the current session."""
    events = db.query(EventRecord).filter(EventRecord.session_id == session_id).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "event_type": e.event_type,
            "guest_count": e.guest_count,
            "total_budget": e.total_budget,
            "event_date": e.event_date,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]
