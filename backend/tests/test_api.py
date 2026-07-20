def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_complete_automatic_refund_and_incident_flow(client):
    customers = client.get("/api/v1/customers").json()
    assert len(customers) == 3

    response = client.post(
        "/api/v1/chat/messages",
        json={
            "customer_id": "cust-kumar",
            "message": ("Bhai payment deduct ho gaya but order confirm nahi hua."),
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "failed_payment"
    assert payload["action"]["status"] == "completed"
    assert payload["incident"] is not None
    assert payload["decision_mode"] == "automatic"
    assert payload["risk_level"] == "low"
    assert len(payload["resolution_trace"]) == 6

    transactions = client.get("/api/v1/transactions?customer_id=cust-kumar").json()
    assert transactions[0]["status"] == "refunded"

    incidents = client.get("/api/v1/incidents").json()
    assert len(incidents) == 1

    updated = client.post(
        f"/api/v1/incidents/{incidents[0]['id']}/status",
        json={"status": "investigating"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "investigating"


def test_approval_flow(client):
    response = client.post(
        "/api/v1/chat/messages",
        json={
            "customer_id": "cust-aarav",
            "message": ("I need a refund because payment succeeded but no order was created."),
        },
    )
    assert response.status_code == 200, response.text
    action = response.json()["action"]
    assert action["status"] == "awaiting_approval"

    approved = client.post(
        f"/api/v1/actions/{action['id']}/approve",
        json={"comment": "Evidence verified"},
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "completed"


def test_duplicate_message_does_not_duplicate_refund(client):
    body = {
        "customer_id": "cust-kumar",
        "message": ("Bhai payment deduct ho gaya but order confirm nahi hua."),
    }
    first = client.post("/api/v1/chat/messages", json=body)
    second = client.post("/api/v1/chat/messages", json=body)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["action"]["id"] == second.json()["action"]["id"]


def test_demo_reset_restores_original_synthetic_state(client):
    body = {
        "customer_id": "cust-kumar",
        "message": "Bhai payment deduct ho gaya but order confirm nahi hua.",
    }
    completed = client.post("/api/v1/chat/messages", json=body)
    assert completed.json()["action"]["status"] == "completed"

    reset = client.post("/api/v1/demo/reset")
    assert reset.status_code == 200, reset.text
    assert reset.json()["status"] == "ready"

    transactions = client.get("/api/v1/transactions?customer_id=cust-kumar").json()
    assert transactions[0]["status"] == "success"
    assert client.get("/api/v1/actions").json() == []
    assert client.get("/api/v1/incidents").json() == []
