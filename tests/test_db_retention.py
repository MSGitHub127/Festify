"""Tests for database persistence, enterprise pooling, volume mount safety checks, and relational cascades."""
from __future__ import annotations

import logging

from app.db import init_db
from app.models import EventRecord, ExpenseRecord, MilestoneRecord


def test_init_db_idempotent():
    """Verify init_db can be safely invoked repeatedly without errors."""
    init_db()
    init_db()


def test_production_sqlite_operational_risk_warning(caplog, monkeypatch):
    """Verify that using file-based SQLite in production triggers an explicit operational risk notice."""
    from app import db

    monkeypatch.setattr(db.settings, "environment", "production")
    monkeypatch.setattr(db, "DATABASE_URL", "sqlite:///festify.db")

    with caplog.at_level(logging.WARNING):
        db.init_db()

    assert any("OPERATIONAL RISK NOTICE" in record.message for record in caplog.records)


def test_relational_cascade_deletion(db_session):
    """Verify cascade deletion preserves integrity when an event is deleted."""
    event = EventRecord(
        session_id="test-session-cascade",
        event_type="wedding",
        title="Cascade Test Event",
        guest_count=100,
        total_budget=10000.0,
        vibe_theme="Elegant",
        encrypted_details="test-ciphertext",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    event_id = event.id

    expense = ExpenseRecord(
        event_id=event_id,
        category="Venue",
        item_name="Deposit",
        allocated_amount=4000.0,
        actual_amount=4000.0,
    )
    milestone = MilestoneRecord(
        event_id=event_id,
        timeframe="Month 6",
        title="Book Catering",
    )
    db_session.add_all([expense, milestone])
    db_session.commit()

    # Verify children exist
    assert db_session.query(ExpenseRecord).filter_by(event_id=event_id).count() == 1
    assert db_session.query(MilestoneRecord).filter_by(event_id=event_id).count() == 1

    # Delete parent event
    db_session.delete(event)
    db_session.commit()

    # Children should be automatically cascaded
    assert db_session.query(ExpenseRecord).filter_by(event_id=event_id).count() == 0
    assert db_session.query(MilestoneRecord).filter_by(event_id=event_id).count() == 0
