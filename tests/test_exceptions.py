"""Tests for custom domain exception hierarchy and centralized error handlers."""
from __future__ import annotations

from app.exceptions import (
    BudgetCalculationError,
    EventNotFoundError,
    SecurityValidationError,
    StatutoryPermitError,
)


def test_exception_status_codes():
    """Verify that domain exceptions assign correct HTTP status codes."""
    not_found = EventNotFoundError("evt-test-123")
    assert not_found.status_code == 404
    assert "evt-test-123" in not_found.message

    budget_err = BudgetCalculationError("Invalid allocation sum")
    assert budget_err.status_code == 422

    permit_err = StatutoryPermitError("Unknown jurisdiction")
    assert permit_err.status_code == 400

    sec_err = SecurityValidationError("Invalid signature")
    assert sec_err.status_code == 401


def test_global_exception_handler_integration(client):
    """Verify that raising a domain exception returns formatted JSON response via FastAPI handler."""
    # Attempting to fetch non-existent event triggers EventNotFoundError
    res = client.get("/api/events/non-existent-random-id-999")
    assert res.status_code == 404
    assert "non-existent-random-id-999" in res.json()["detail"]

    # Budget for non-existent event
    b_res = client.get("/api/events/non-existent-random-id-999/budget")
    assert b_res.status_code == 404
    assert "not found" in b_res.json()["detail"].lower()
