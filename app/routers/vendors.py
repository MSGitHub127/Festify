"""Vendor checklists, vetting questions, and contract risk endpoints."""
from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import EventRecord, VendorChecklistItem
from app.planner.vendor_rubric import get_vendor_checklists
from app.security import decrypt_data

router = APIRouter(prefix="/api", tags=["Vendors"])


@router.get("/vendors/rubric", response_model=list[VendorChecklistItem])
def get_rubric_checklists(
    event_type: str = Query(default="wedding", description="Event type: wedding, birthday, community"),
) -> list[VendorChecklistItem]:
    """Retrieve category-specific vendor checklists and contract red flags."""
    return get_vendor_checklists(event_type)


@router.get("/events/{event_id}/vendors", response_model=list[VendorChecklistItem])
def get_event_vendor_checklists(event_id: str, db: Annotated[Session, Depends(get_db)]) -> list[VendorChecklistItem]:
    """Retrieve vendor vetting checklists for a saved event."""
    record = db.get(EventRecord, event_id)
    if not record or not record.encrypted_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    decrypted = json.loads(decrypt_data(record.encrypted_details))
    return [VendorChecklistItem(**v) for v in decrypted["vendor_rubric"]]
