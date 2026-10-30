"""Domain-specific exception hierarchy for Festify."""
from __future__ import annotations


class FestifyBaseException(Exception):
    """Base exception class for all Festify application errors."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class EventNotFoundError(FestifyBaseException):
    """Raised when a requested event record cannot be located in the persistence store."""

    def __init__(self, event_id: str) -> None:
        super().__init__(f"Event plan with ID '{event_id}' was not found.", status_code=404)
        self.event_id = event_id


class BudgetCalculationError(FestifyBaseException):
    """Raised when budget parameters or guest counts violate mathematical constraints."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)


class StatutoryPermitError(FestifyBaseException):
    """Raised when permit rules cannot be evaluated for an unrecognized jurisdiction or event type."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class SecurityValidationError(FestifyBaseException):
    """Raised when authentication tokens or encrypted records fail cryptographic verification."""

    def __init__(self, message: str = "Cryptographic security verification failed.") -> None:
        super().__init__(message, status_code=401)
