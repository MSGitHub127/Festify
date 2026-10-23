"""Tests for statutory permits, alcohol licensing, noise ordinances, and capacity safety."""
from __future__ import annotations

from app.planner.permit_rules import evaluate_statutory_permits


def test_community_event_permits():
    permits = evaluate_statutory_permits("community", guest_count=800, location="City Central Park")

    assert permits.sound_permit_required is True
    assert "Special One-Day Event Liquor License" in permits.alcohol_license_notes
    assert "Temporary Food Facility (TFF)" in permits.food_handling_hygiene
    assert "800" in permits.fire_capacity_regulations
    assert "weather contingency" in permits.weather_backup_plan.lower()


def test_wedding_permits_large_outdoor():
    permits = evaluate_statutory_permits("wedding", guest_count=180, location="Outdoor Botanical Gardens")

    assert permits.sound_permit_required is True
    assert "liquor liability" in permits.alcohol_license_notes.lower()
    assert "180" in permits.fire_capacity_regulations
    assert "weather call" in permits.weather_backup_plan.lower()


def test_wedding_permits_small_indoor():
    permits = evaluate_statutory_permits("wedding", guest_count=60, location="Indoor Historic Manor")

    assert permits.sound_permit_required is False
    assert "banquet" in permits.fire_capacity_regulations.lower()


def test_birthday_permits():
    permits = evaluate_statutory_permits("birthday", guest_count=35, location="Private Loft")

    assert permits.sound_permit_required is False
    assert "umbrella" in permits.alcohol_license_notes.lower()
    assert "35" in permits.fire_capacity_regulations
