"""Shared pytest fixtures for the backend tests."""

from __future__ import annotations

import base64
import shutil
import sys
from pathlib import Path

import pytest

# Resolve the backend directory (where api.py, populate_pptx.py, etc. live).
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture()
def backend_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated working directory and switch into it.

    Args:
        tmp_path: Pytest temp directory.
        monkeypatch: Utility to change process state (cwd).

    Returns:
        The temporary working directory.
    """
    (tmp_path / "data" / "input").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "api").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prompt_dictionary").mkdir(parents=True, exist_ok=True)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def coe_tower_json(backend_cwd: Path) -> Path:
    """Copy ``coe_tower.json`` to the path expected by the app.

    Args:
        backend_cwd: Temporary working directory.

    Returns:
        Destination path inside the temp directory.

    Raises:
        FileNotFoundError: If the source file is missing in the repo.
    """
    src = BACKEND_ROOT / "api" / "coe_tower.json"
    if not src.exists():
        raise FileNotFoundError(f"coe_tower.json not found at: {src}")

    dst = backend_cwd / "api" / "coe_tower.json"
    shutil.copyfile(src, dst)
    return dst


@pytest.fixture()
def template_digicore(backend_cwd: Path) -> Path:
    """Copy the DigiCore PPTX template to ``data/input/``.

    Args:
        backend_cwd: Temporary working directory.

    Returns:
        Destination path inside the temp directory.

    Raises:
        FileNotFoundError: If the template file is missing in the repo.
    """
    src = BACKEND_ROOT / "data" / "input" / "SC&O TEMPLATE DigiCore.pptx"
    if not src.exists():
        available = list((BACKEND_ROOT / "data" / "input").glob("*.pptx"))
        raise FileNotFoundError(
            "Template not found at: "
            f"{src}\nAvailable PPTX files in backend/data/input/: "
            f"{[p.name for p in available]}"
        )

    dst = backend_cwd / "data" / "input" / "SC&O TEMPLATE DigiCore.pptx"
    shutil.copyfile(src, dst)
    return dst


@pytest.fixture()
def minimal_pdf_b64() -> str:
    """Return a tiny valid PDF as a base64 string."""
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
    return base64.b64encode(pdf_bytes).decode("utf-8")
