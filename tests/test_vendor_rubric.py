"""Tests for vendor vetting questions, deliverable milestones, and contract red flag detection."""
from __future__ import annotations

from app.planner.vendor_rubric import get_vendor_checklists


def test_wedding_vendor_checklists():
    items = get_vendor_checklists("wedding")
    assert len(items) >= 4

    categories = [i.category for i in items]
    assert any("Catering" in c for c in categories)
    assert any("Photography" in c for c in categories)
    assert any("Music" in c for c in categories)
    assert any("Floral" in c for c in categories)

    for item in items:
        assert len(item.must_ask_questions) >= 3
        assert len(item.contract_red_flags) >= 2
        assert len(item.deliverable_milestones) >= 3
        assert item.benchmark_percentage > 0.0


def test_birthday_vendor_checklists():
    items = get_vendor_checklists("birthday")
    assert len(items) >= 2

    categories = [i.category for i in items]
    assert any("Venue" in c for c in categories)
    assert any("Bakery" in c for c in categories)

    cake_item = next(i for i in items if "Bakery" in i.category)
    assert any("allergi" in q.lower() for q in cake_item.must_ask_questions)


def test_community_vendor_checklists():
    items = get_vendor_checklists("community")
    assert len(items) >= 2

    categories = [i.category for i in items]
    assert any("Stage" in c or "Sound" in c for c in categories)
    assert any("Sanitation" in c for c in categories)


def test_vendor_checklists_fallback():
    items = get_vendor_checklists("unknown_event_type")
    assert len(items) >= 4  # falls back to wedding
