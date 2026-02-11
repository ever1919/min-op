"""Integration tests for the /generate-onepager endpoint."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

import api


def test_invalid_base64(coe_tower_json, backend_cwd):
    """Invalid base64 payload returns HTTP 400."""
    client = TestClient(api.app)
    payload = {
        "file": "NOT_BASE64!!!",
        "filename": "cv.pdf",
        "coe_selected": "Digi Core",
        "tower_selected": "Control Tower",
    }

    response = client.post("/generate-onepager", json=payload)

    assert response.status_code == 400
    assert "Invalid base64 file" in response.text


def test_returns_pptx(
    coe_tower_json,
    template_digicore,
    backend_cwd,
    minimal_pdf_b64,
    monkeypatch,
):
    """Valid request returns a PPTX stream."""
    monkeypatch.setattr(api, "BASE_DIR", Path.cwd(), raising=False)

    def fake_generate_one_pager(
        pdf_path: str,
        coe_selected: str,
        tower_selected: str,
        save_debug: bool = True,
    ) -> pd.DataFrame:
        """Return deterministic sections for rendering."""
        return pd.DataFrame(
            [
                {"section_name": "NAME", "output": "Jane Doe"},
                {"section_name": "TOWER", "output": tower_selected},
                {"section_name": "PROFILE OVERVIEW", "output": "Short summary."},
            ]
        )

    monkeypatch.setattr(api.gen, "generate_one_pager", fake_generate_one_pager)

    client = TestClient(api.app)
    payload = {
        "file": minimal_pdf_b64,
        "filename": "cv.pdf",
        "coe_selected": "Digi Core",
        "tower_selected": "Control Tower",
    }

    response = client.post("/generate-onepager", json=payload)

    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert len(response.content) > 1000
