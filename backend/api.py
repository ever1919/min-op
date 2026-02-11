"""FastAPI backend for generating a CV one-pager PowerPoint.

This service receives a base64-encoded PDF resume, generates structured content
via the CV processing pipeline, and returns a populated PPTX as a streamed
download.
"""

import base64
import json
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import cv_process_sort_gen as gen
import populate_pptx as pptx


# Ensure relative paths inside backend package resolve correctly
BASE_DIR = Path(__file__).resolve().parent

# Optional override for runtime deployments (e.g., when mounting files elsewhere).
# If not set, defaults to BASE_DIR.
APP_ROOT = Path(os.environ.get("APP_ROOT", str(BASE_DIR))).resolve()

# Canonical filesystem locations used by this API.
API_DIR = APP_ROOT / "api"
DATA_DIR = APP_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
COE_TOWER_PATH = API_DIR / "coe_tower.json"


class GenerateRequest(BaseModel):
    """Request payload for generating a one-pager presentation.

    Attributes:
        file: Base64-encoded PDF content.
        filename: Original filename for the uploaded PDF.
        coe_selected: Selected center of excellence identifier.
        tower_selected: Selected tower identifier.
    """

    file: str
    filename: str
    coe_selected: str
    tower_selected: str


app = FastAPI(title="CV One-Pager API")

# Allow local frontend access; change origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        A small status payload indicating the service is running.
    """
    return {"status": "ok"}

@app.get("/api/coe-towers")
def get_coe_towers() -> dict:
    """Load and return the COE to tower mapping.

    The mapping is read from a JSON file located at api/coe_tower.json relative
    to this module's directory.

    Returns:
        The parsed JSON mapping as a dictionary.

    Raises:
        HTTPException: If the file cannot be found or the JSON is invalid.
    """
    try:
        with COE_TOWER_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="COE Tower mapping file not found",
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON format",
        ) from exc

@app.post("/generate-onepager")
async def generate_onepager(req: GenerateRequest) -> FileResponse:
    """Generate a one-pager PPTX from an uploaded PDF resume.

    This endpoint:
    - Decodes a base64 PDF payload and saves it under data/input
    - Generates structured content via the one-pager pipeline
    - Populates a PPTX template and streams it back to the client
    - Removes the uploaded PDF after processing

    Args:
        req: Request payload containing the base64 PDF and selection metadata.

    Returns:
        A FileResponse that downloads the generated PPTX.

    Raises:
        HTTPException: If required fields are missing, the input is invalid,
            file operations fail, or the one-pager generation fails.
    """
    print(f"Received COE: {req.coe_selected}")
    print(f"Received Tower: {req.tower_selected}")

    if not req.coe_selected or not req.tower_selected:
        raise HTTPException(
            status_code=400,
            detail=(
                "Missing COE or Tower. "
                f"req Received: coe={req.coe_selected}, tower={req.tower_selected}"
            ),
        )

    # Decode file payload.
    try:
        pdf_bytes = base64.b64decode(req.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid base64 file: {exc}") from exc

    # Ensure IO directories exist.
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Prevent path traversal by using only the final path component.
    safe_filename = Path(req.filename).name
    if not safe_filename:
        safe_filename = "cv.pdf"

    pdf_path = INPUT_DIR / req.filename

    try:
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed saving file: {exc}") from exc

    try:
        df = gen.generate_one_pager(
            str(pdf_path),
            req.coe_selected,
            req.tower_selected,
            save_debug=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generating one-pager: {exc}") from exc

    try:
        # populate_pptx may return a relative path; resolve it under APP_ROOT.
        pptx_path = Path(pptx.populate_pptx(df, req.coe_selected))

        if pptx_path.is_absolute():
            full_pptx_path = pptx_path
        else:
            full_pptx_path = APP_ROOT / pptx_path

        if not full_pptx_path.exists():
            raise FileNotFoundError(str(full_pptx_path))

        return FileResponse(
            path=str(full_pptx_path),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=full_pptx_path.name,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error creating PPTX: {exc}") from exc
    finally:
        # Always attempt to remove the uploaded file after processing.
        try:
            if pdf_path.exists():
                pdf_path.unlink()
                print(f"Removed uploaded PDF: {pdf_path}")
        except Exception as cleanup_err:
            print(f"Failed to remove uploaded PDF {pdf_path}: {cleanup_err}")


if __name__ == "__main__":
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)