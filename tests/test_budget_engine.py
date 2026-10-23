"""Tests for the algorithmic budget allocation, cost variance, and savings engine."""
from __future__ import annotations

from app.planner.budget_engine import (
    analyze_budget_variance,
    generate_budget_breakdown,
)


def test_wedding_budget_breakdown():
    total_budget = 30000.0
    guests = 150
    breakdown = generate_budget_breakdown("wedding", total_budget, guests)

    assert breakdown.total_budget == total_budget
    assert breakdown.guest_count == guests
    assert breakdown.cost_per_guest == 200.0
    assert breakdown.contingency_buffer == 3000.0  # 10%
    assert len(breakdown.categories) == 7

    # Sum of percentages should equal 100%
    total_percent = sum(c.percentage for c in breakdown.categories)
    assert abs(total_percent - 100.0) < 0.1

    # Sum of allocated amounts should equal total budget
    total_allocated = sum(c.allocated_amount for c in breakdown.categories)
    assert abs(total_allocated - total_budget) < 1.0

    # Ensure venue and catering is the largest slice (45%)
    venue_cat = next(c for c in breakdown.categories if "Venue" in c.category)
    assert venue_cat.percentage == 45.0
    assert venue_cat.allocated_amount == 13500.0

    # Check saving tips
    assert len(breakdown.cost_saving_tips) >= 3


def test_birthday_budget_breakdown():
    total_budget = 5000.0
    guests = 50
    breakdown = generate_budget_breakdown("birthday", total_budget, guests)

    assert breakdown.cost_per_guest == 100.0
    assert breakdown.contingency_buffer == 500.0  # 10%

    total_percent = sum(c.percentage for c in breakdown.categories)
    assert abs(total_percent - 100.0) < 0.1

    # Birthday includes Catering & Signature Cake as 35%
    cake_cat = next(c for c in breakdown.categories if "Catering" in c.category)
    assert cake_cat.percentage == 35.0
    assert cake_cat.allocated_amount == 1750.0


def test_community_budget_breakdown():
    total_budget = 50000.0
    guests = 1000
    breakdown = generate_budget_breakdown("community", total_budget, guests)

    assert breakdown.cost_per_guest == 50.0
    assert breakdown.contingency_buffer == 5000.0

    total_percent = sum(c.percentage for c in breakdown.categories)
    assert abs(total_percent - 100.0) < 0.1

    # Community includes Municipal Park Permits and Public Safety
    safety_cat = next(c for c in breakdown.categories if "Safety" in c.category)
    assert safety_cat.percentage == 15.0
    assert safety_cat.allocated_amount == 7500.0


def test_budget_breakdown_edge_case_zero_guests():
    breakdown = generate_budget_breakdown("wedding", 10000.0, 0)
    assert breakdown.cost_per_guest == 10000.0
    assert breakdown.contingency_buffer == 1000.0


def test_budget_breakdown_fallback_unknown_type():
    breakdown = generate_budget_breakdown("unknown_festival", 20000.0, 100)
    assert len(breakdown.categories) == 7
    assert breakdown.contingency_buffer == 2000.0


def test_analyze_budget_variance_over_budget():
    res = analyze_budget_variance(allocated=1000.0, actual=1250.0)
    assert res["status"] == "over_budget"
    assert res["difference"] == 250.0
    assert res["percent_variance"] == 25.0
    assert "exceeds" in str(res["alert"])


def test_analyze_budget_variance_under_budget():
    res = analyze_budget_variance(allocated=2000.0, actual=1600.0)
    assert res["status"] == "under_budget"
    assert res["difference"] == -400.0
    assert res["percent_variance"] == -20.0
    assert "savings" in str(res["alert"])


def test_analyze_budget_variance_on_target():
    res = analyze_budget_variance(allocated=3000.0, actual=3000.0)
    assert res["status"] == "on_target"
    assert res["difference"] == 0.0
    assert res["percent_variance"] == 0.0
    assert "matches" in str(res["alert"])
