"""Budget allocation and cost variance REST endpoints."""
from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.exceptions import EventNotFoundError
from app.models import BudgetBreakdown, EventRecord, VarianceAnalysisResponse
from app.planner.budget_engine import analyze_budget_variance, generate_budget_breakdown
from app.security import decrypt_data

router = APIRouter(prefix="/api", tags=["Budget"])


class VarianceCheckRequest(BaseModel):
    """Request payload for comparing allocated budget against vendor quotes."""

    category: str = Field(default="General", description="Expense category name")
    allocated_amount: float = Field(default=0.0, ge=0.0, description="Allocated budget amount")
    actual_quote_amount: float = Field(default=0.0, ge=0.0, description="Actual quoted vendor amount")
    allocated: float | None = Field(default=None, description="Alias for allocated_amount")
    actual: float | None = Field(default=None, description="Alias for actual_quote_amount")
    allocated_budget: float | None = Field(default=None, description="Alias for allocated_amount")
    actual_quote: float | None = Field(default=None, description="Alias for actual_quote_amount")

    def get_allocated(self) -> float:
        """Resolve the allocated amount across possible field aliases."""
        for val in (self.allocated_amount, self.allocated, self.allocated_budget):
            if val is not None and val > 0:
                return val
        return self.allocated_amount

    def get_actual(self) -> float:
        """Resolve the actual quoted amount across possible field aliases."""
        for val in (self.actual_quote_amount, self.actual, self.actual_quote):
            if val is not None and val > 0:
                return val
        return self.actual_quote_amount


class StatelessBudgetRequest(BaseModel):
    """Request payload for on-the-fly mathematical budget generation."""

    event_type: str = Field(default="wedding", description="Celebration type: wedding, birthday, or community")
    total_budget: float = Field(default=15000.0, ge=100.0, description="Total budget in USD")
    guest_count: int = Field(default=100, ge=1, description="Estimated guest count")


@router.post("/budget/calculate", response_model=BudgetBreakdown)
def calculate_stateless_budget(request: StatelessBudgetRequest) -> BudgetBreakdown:
    """Instantly calculate an algorithmic category budget breakdown.

    Args:
        request: Parameters including celebration type, budget cap, and attendee count.

    Returns:
        Structured BudgetBreakdown with allocations, per-guest math, and 10% contingency.
    """
    return generate_budget_breakdown(request.event_type, request.total_budget, request.guest_count)


@router.post("/budget/variance", response_model=VarianceAnalysisResponse)
def calculate_stateless_variance(request: VarianceCheckRequest) -> VarianceAnalysisResponse:
    """Stateless budget variance evaluator between allocation and vendor quote.

    Args:
        request: Allocated budget and actual quote figures.

    Returns:
        VarianceAnalysisResponse with variance dollar difference, percentage, and alert.
    """
    res = analyze_budget_variance(request.get_allocated(), request.get_actual())
    return VarianceAnalysisResponse(**res)


@router.get("/events/{event_id}/budget", response_model=BudgetBreakdown)
def get_event_budget(event_id: str, db: Annotated[Session, Depends(get_db)]) -> BudgetBreakdown:
    """Retrieve the budget breakdown for an existing stored event.

    Args:
        event_id: Unique event identifier.
        db: SQLAlchemy database session.

    Returns:
        Decrypted and deserialized BudgetBreakdown schema.

    Raises:
        EventNotFoundError: If no event record matching event_id is found.
    """
    record = db.get(EventRecord, event_id)
    if not record or not record.encrypted_details:
        raise EventNotFoundError(event_id)

    decrypted = json.loads(decrypt_data(record.encrypted_details))
    return BudgetBreakdown(**decrypted["budget"])


@router.post("/events/{event_id}/budget/variance", response_model=VarianceAnalysisResponse)
def check_quote_variance(
    event_id: str,
    request: VarianceCheckRequest,
    db: Annotated[Session, Depends(get_db)],
) -> VarianceAnalysisResponse:
    """Evaluate whether a vendor's price quote deviates from the event's allocated budget.

    Args:
        event_id: Target event ID.
        request: Variance request with allocated and actual amounts.
        db: SQLAlchemy database session.

    Returns:
        VarianceAnalysisResponse with status, variance amount, and optimization tip.

    Raises:
        EventNotFoundError: If event cannot be located.
    """
    record = db.get(EventRecord, event_id)
    if not record:
        raise EventNotFoundError(event_id)

    res = analyze_budget_variance(request.get_allocated(), request.get_actual())
    return VarianceAnalysisResponse(**res)
