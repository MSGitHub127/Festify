"""Tests for event scenario comparison, tradeoff analysis, and guest economic differentials."""
from __future__ import annotations


def test_compare_scenarios_endpoint(client, auth_headers):
    payload = {
        "scenario_a": {
            "name": "Estate Ballroom",
            "event_type": "wedding",
            "total_budget": 30000.0,
            "guest_count": 100,
            "venue_style": "Indoor Ballroom",
        },
        "scenario_b": {
            "name": "Botanical Greenhouse",
            "event_type": "wedding",
            "total_budget": 36000.0,
            "guest_count": 150,
            "venue_style": "Glass Greenhouse",
        },
    }

    res = client.post("/api/events/compare", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    assert data["scenario_a_name"] == "Estate Ballroom"
    assert data["scenario_b_name"] == "Botanical Greenhouse"
    assert data["total_budget_diff"] == 6000.0
    assert data["guest_count_diff"] == 50

    # Scenario A: 30000 / 100 = 300.00 / guest
    # Scenario B: 36000 / 150 = 240.00 / guest
    # Diff: 240 - 300 = -60.00
    assert data["cost_per_guest_diff"] == -60.0

    # Check category diffs
    assert len(data["category_diffs"]) == 7
    venue_diff = next(c for c in data["category_diffs"] if "Venue" in c["category"])
    assert venue_diff["scenario_a_amount"] == 13500.0
    assert venue_diff["scenario_b_amount"] == 16200.0
    assert venue_diff["difference"] == 2700.0

    # Check recommendation
    assert "better per-guest economic efficiency" in data["recommendation"]
