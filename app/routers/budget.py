"""Budget allocation and cost variance REST endpoints."""
from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import BudgetBreakdown, EventRecord
from app.planner.budget_engine import analyze_budget_variance, generate_budget_breakdown
from app.security import decrypt_data

router = APIRouter(prefix="/api", tags=["Budget"])


class VarianceCheckRequest(BaseModel):
    category: str = Field(default="General")
    allocated_amount: float = Field(default=0.0, ge=0.0)
    actual_quote_amount: float = Field(default=0.0, ge=0.0)
    allocated: float | None = None
    actual: float | None = None
    allocated_budget: float | None = None
    actual_quote: float | None = None

    def get_allocated(self) -> float:
        for val in (self.allocated_amount, self.allocated, self.allocated_budget):
            if val is not None and val > 0:
                return val
        return self.allocated_amount

    def get_actual(self) -> float:
        for val in (self.actual_quote_amount, self.actual, self.actual_quote):
            if val is not None and val > 0:
                return val
        return self.actual_quote_amount


class StatelessBudgetRequest(BaseModel):
    event_type: str = Field(default="wedding")
    total_budget: float = Field(default=15000.0, ge=100.0)
    guest_count: int = Field(default=100, ge=1)


@router.post("/budget/calculate", response_model=BudgetBreakdown)
def calculate_stateless_budget(request: StatelessBudgetRequest) -> BudgetBreakdown:
    """Instantly calculate an algorithmic category budget breakdown."""
    return generate_budget_breakdown(request.event_type, request.total_budget, request.guest_count)


@router.post("/budget/variance")
def calculate_stateless_variance(request: VarianceCheckRequest) -> dict:
    """Stateless budget variance evaluator."""
    return analyze_budget_variance(request.get_allocated(), request.get_actual())


@router.get("/events/{event_id}/budget", response_model=BudgetBreakdown)
def get_event_budget(event_id: str, db: Annotated[Session, Depends(get_db)]) -> BudgetBreakdown:
    """Retrieve the budget breakdown for an existing event."""
    record = db.get(EventRecord, event_id)
    if not record or not record.encrypted_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    decrypted = json.loads(decrypt_data(record.encrypted_details))
    return BudgetBreakdown(**decrypted["budget"])


@router.post("/events/{event_id}/budget/variance")
def check_quote_variance(
    event_id: str,
    request: VarianceCheckRequest,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Evaluate whether a vendor's price quote deviates significantly from the allocated budget."""
    record = db.get(EventRecord, event_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    return analyze_budget_variance(request.get_allocated(), request.get_actual())
