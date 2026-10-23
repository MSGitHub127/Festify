"""Timeline, milestone countdown, and run-of-show endpoints."""
from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import EventRecord, TimelinePlan
from app.planner.timeline_engine import generate_timeline_plan
from app.security import decrypt_data

router = APIRouter(prefix="/api", tags=["Timeline"])


class StatelessTimelineRequest(BaseModel):
    event_type: str = Field(default="wedding")


@router.post("/timeline/generate", response_model=TimelinePlan)
def generate_stateless_timeline(request: StatelessTimelineRequest) -> TimelinePlan:
    """Instantly generate macro milestones and day-of run-of-show."""
    return generate_timeline_plan(request.event_type)


@router.get("/events/{event_id}/timeline", response_model=TimelinePlan)
def get_event_timeline(event_id: str, db: Annotated[Session, Depends(get_db)]) -> TimelinePlan:
    """Retrieve the timeline plan for a saved event."""
    record = db.get(EventRecord, event_id)
    if not record or not record.encrypted_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    decrypted = json.loads(decrypt_data(record.encrypted_details))
    return TimelinePlan(**decrypted["timeline"])
