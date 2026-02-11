"""Tests for the /health endpoint."""

from fastapi.testclient import TestClient

import api


def test_ok(backend_cwd):
    """Health endpoint returns OK."""
    client = TestClient(api.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
