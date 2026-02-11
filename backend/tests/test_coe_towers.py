"""Tests for the /api/coe-towers endpoint."""

from fastapi.testclient import TestClient

import api


def test_returns_json(coe_tower_json, backend_cwd):
    """COE towers endpoint returns a JSON mapping."""
    client = TestClient(api.app)

    response = client.get("/api/coe-towers")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, dict)
    assert "Digi Core" in data
    assert isinstance(data["Digi Core"], list)
    assert "Control Tower" in data["Digi Core"]
