from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import base64
import io
import os
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
    flavor: Optional[str] = None
    tower: Optional[str] = None


app = FastAPI(title="CV One-Pager API")

# Allow local frontend access; change origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "alive", "message": "Backend is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/generate-onepager")
async def generate_onepager(req: GenerateRequest):
    """Accepts a base64 PDF and filename, runs the generator and returns a PPTX file.

    Request JSON: { file: base64string, filename: string, flavor?: string, tower?: string }
    Response: PPTX binary as attachment
    """
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
        excel_out = output_dir / "one_pager_summary.xlsx"
        df = gen.generate_one_pager(str(pdf_path), req.flavor, req.tower, output_path=str(excel_out))
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)
