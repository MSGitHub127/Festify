"""End-to-end integration API flow tests for Festify."""
from __future__ import annotations


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Festify" in data["app"]


def test_anonymous_session_generation(client):
    response = client.post("/api/session")
    assert response.status_code == 200
    data = response.json()
    assert "festify-" in data["session_id"]
    assert len(data["token"]) > 20
    assert data["expires_in_minutes"] == 120


def test_complete_event_lifecycle(client, auth_headers, sample_wedding_payload):
    # 1. Create Event Plan
    create_res = client.post("/api/events", json=sample_wedding_payload, headers=auth_headers)
    assert create_res.status_code == 201
    event_data = create_res.json()

    event_id = event_data["event_id"]
    assert event_id is not None
    assert event_data["title"] == sample_wedding_payload["title"]
    assert event_data["total_budget"] == sample_wedding_payload["total_budget"]

    # Verify nested domain objects
    assert "budget" in event_data
    assert event_data["budget"]["cost_per_guest"] == round(28000.0 / 120, 2)
    assert len(event_data["budget"]["categories"]) == 7

    assert "timeline" in event_data
    assert len(event_data["timeline"]["macro_milestones"]) >= 6
    assert len(event_data["timeline"]["day_of_run_of_show"]) >= 10

    assert "vendor_rubric" in event_data
    assert len(event_data["vendor_rubric"]) >= 4

    assert "creative_ideas" in event_data
    assert len(event_data["creative_ideas"]["themes"]) >= 3

    assert "statutory_permits" in event_data
    assert "client_dossier_markdown" in event_data
    assert "Festify Event Dossier" in event_data["client_dossier_markdown"]

    # 2. Retrieve Event Plan by ID
    get_res = client.get(f"/api/events/{event_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["event_id"] == event_id

    # 3. Retrieve Event List
    list_res = client.get("/api/events", headers=auth_headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(item["id"] == event_id for item in items)

    # 4. Ask Grounded Question
    qa_res = client.post(
        f"/api/events/{event_id}/ask",
        json={"question": "When does the photographer arrive for portraits?"},
        headers=auth_headers,
    )
    assert qa_res.status_code == 200
    qa_data = qa_res.json()
    assert "answer" in qa_data
    assert len(qa_data["answer"]) > 10

    # 5. Export Dossier Markdown
    dossier_res = client.get(f"/api/events/{event_id}/dossier", headers=auth_headers)
    assert dossier_res.status_code == 200
    assert "text/markdown" in dossier_res.headers.get("content-type", "")
    assert "Festify Event Dossier" in dossier_res.text


def test_standalone_budget_and_variance_endpoints(client, auth_headers):
    # Standalone Budget Calculation
    calc_res = client.post(
        "/api/budget/calculate",
        json={"event_type": "birthday", "total_budget": 5000.0, "guest_count": 50},
        headers=auth_headers,
    )
    assert calc_res.status_code == 200
    b_data = calc_res.json()
    assert b_data["cost_per_guest"] == 100.0
    assert b_data["contingency_buffer"] == 500.0

    # Standalone Variance Analysis
    var_res = client.post(
        "/api/budget/variance",
        json={"allocated_budget": 2000.0, "actual_quote": 2400.0},
        headers=auth_headers,
    )
    assert var_res.status_code == 200
    v_data = var_res.json()
    assert v_data["status"] == "over_budget"
    assert v_data["difference"] == 400.0


def test_standalone_timeline_and_vendor_endpoints(client, auth_headers):
    # Standalone Timeline
    time_res = client.post(
        "/api/timeline/generate",
        json={"event_type": "community"},
        headers=auth_headers,
    )
    assert time_res.status_code == 200
    t_data = time_res.json()
    assert len(t_data["day_of_run_of_show"]) >= 7

    # Standalone Vendor Rubrics
    vend_res = client.get("/api/vendors/rubric?event_type=wedding", headers=auth_headers)
    assert vend_res.status_code == 200
    assert len(vend_res.json()) >= 4


def test_standalone_ideas_endpoint(client, auth_headers):
    res = client.post(
        "/api/ideas/generate",
        json={"event_type": "birthday", "vibe_theme": "Speakeasy Glam"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["themes"]) >= 3
    assert len(data["curated_menu"]) >= 3


def test_serve_frontend_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Festify" in response.text
    assert '<main id="main"' in response.text


def test_event_not_found_handling(client, auth_headers):
    response = client.get("/api/events/non-existent-uuid-12345", headers=auth_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_invalid_payload_validation(client, auth_headers):
    # Budget less than min (100)
    invalid_payload = {
        "title": "Tiny Budget Party",
        "event_type": "birthday",
        "total_budget": 20.0,
        "guest_count": 10,
    }
    response = client.post("/api/events", json=invalid_payload, headers=auth_headers)
    assert response.status_code == 422
