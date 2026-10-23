"""Tests for the run-of-show timeline engine, countdown milestones, and conflict detector."""
from __future__ import annotations

from app.models import RunOfShowItem
from app.planner.timeline_engine import (
    detect_timeline_conflicts,
    generate_timeline_plan,
)


def test_wedding_timeline_plan():
    plan = generate_timeline_plan("wedding")

    assert len(plan.macro_milestones) >= 6
    assert len(plan.day_of_run_of_show) >= 10

    # Macro milestones begin 12-9 months out
    assert "12–9 Months Out" in plan.macro_milestones[0].timeframe
    assert "Rehearsal" in plan.macro_milestones[-1].title

    # Day of run of show starts in the morning and ends with send-off
    times = [item.time for item in plan.day_of_run_of_show]
    assert times[0] == "09:00"
    assert times[-1] == "23:00"

    # Specific wedding activities are present
    activities = [item.activity for item in plan.day_of_run_of_show]
    assert any("Ceremony" in act for act in activities)
    assert any("Cocktail" in act for act in activities)
    assert any("Dinner" in act for act in activities)
    assert any("Cake" in act for act in activities)


def test_birthday_timeline_plan():
    plan = generate_timeline_plan("birthday")

    assert len(plan.macro_milestones) >= 4
    assert len(plan.day_of_run_of_show) >= 6

    # Birthday run of show items
    activities = [item.activity for item in plan.day_of_run_of_show]
    assert any("Happy Birthday" in act for act in activities)
    assert any("Games" in act for act in activities)


def test_community_timeline_plan():
    plan = generate_timeline_plan("community")

    assert len(plan.macro_milestones) >= 4
    assert len(plan.day_of_run_of_show) >= 7

    # Community event starts with technical load-in and safety briefing
    activities = [item.activity for item in plan.day_of_run_of_show]
    assert any("Staging" in act or "Technical" in act for act in activities)
    assert any("Volunteer" in act or "Safety" in act for act in activities)


def test_timeline_conflict_detection_simultaneous_activities():
    items = [
        RunOfShowItem(
            time="14:00",
            activity="Guest Arrival & Welcome Cocktail",
            location="Foyer",
            responsible="Host",
            notes="",
        ),
        RunOfShowItem(
            time="14:00",
            activity="Couple Private First Look",
            location="Garden Courtyard",
            responsible="Photographer",
            notes="",
        ),
    ]

    conflicts = detect_timeline_conflicts(items)
    assert len(conflicts) >= 1
    assert "Simultaneous activities scheduled at 14:00" in conflicts[0]


def test_timeline_conflict_detection_no_conflicts():
    items = [
        RunOfShowItem(
            time="14:00",
            activity="Guest Arrival",
            location="Foyer",
            responsible="Host",
            notes="",
        ),
        RunOfShowItem(
            time="15:00",
            activity="Welcome Speech",
            location="Main Hall",
            responsible="Host",
            notes="",
        ),
    ]

    conflicts = detect_timeline_conflicts(items)
    assert len(conflicts) == 0


def test_timeline_plan_fallback():
    plan = generate_timeline_plan("other_unknown_party")
    assert len(plan.macro_milestones) >= 6
    assert len(plan.day_of_run_of_show) >= 10
