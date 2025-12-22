from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import base64
import io
import os
import json
from pathlib import Path
from typing import Optional

import cv_process_sort_gen as gen
import populate_pptx as pptx


# Ensure relative paths inside backend package resolve correctly
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)


class GenerateRequest(BaseModel):
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
async def health():
    return {"status": "ok"}

@app.get("/api/coe-towers")
def get_coe_towers():
    """Return the COE-Tower mapping from JSON file"""
    try:
        with open("api/coe_tower.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="COE Tower mapping file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format")


@app.post("/generate-onepager")
async def generate_onepager(req: GenerateRequest):
    """Generate all sections and return DataFrame.
        
        Args:
        cv_path: Path to input PDF
        coe_selected: Selected COE
        tower_selected: Selected Tower
    
    Returns:
        DataFrame with section_name and output columns
    """
    # Log received parameters
    print(f"✅ Received COE: {req.coe_selected}")
    print(f"✅ Received Tower: {req.tower_selected}")

    if not req.coe_selected or not req.tower_selected:
        raise HTTPException(
            status_code=400,
            detail=f"Missing COE or Tower. Received: coe={req.coe_selected}, tower={req.tower_selected}"
        )

    try:
        # Decode and save uploaded PDF
        data = base64.b64decode(req.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 file: {e}")

    input_dir = BASE_DIR / "data" / "input"
    output_dir = BASE_DIR / "data" / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = input_dir / req.filename
    try:
        with open(pdf_path, "wb") as f:
            f.write(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed saving file: {e}")

    try:
        # Generate one-pager (creates an excel summary and returns a DataFrame)
        df = gen.generate_one_pager(str(pdf_path), req.coe_selected, req.tower_selected, save_debug=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating one-pager: {e}")

    try:
        # Populate PPTX using generated DataFrame
        pptx_path = pptx.populate_pptx(df)
        full_pptx_path = BASE_DIR / pptx_path
        if not full_pptx_path.exists():
            raise FileNotFoundError(str(full_pptx_path))

        # Stream PPTX back to client
        file_like = open(full_pptx_path, "rb")
        return StreamingResponse(file_like, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", headers={
            "Content-Disposition": f"attachment; filename=\"{full_pptx_path.name}\""
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating PPTX: {e}")
    
    finally:
    # Remove only the uploaded PDF to avoid accumulating CVs.
        try:
            if pdf_path.exists():
                pdf_path.unlink()
                print(f"✅ Removed uploaded PDF: {pdf_path}")
        except Exception as cleanup_err:
            print(f"⚠️ Failed to remove uploaded PDF {pdf_path}: {cleanup_err}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)
