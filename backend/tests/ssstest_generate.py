#!/usr/bin/env python3
"""
backend/tests/test_generate.py

Usage:
  python backend/tests/test_generate.py \
    --pdf backend/data/input/sample.pdf \
    --server http://localhost:8000 \
    --out backend/data/output/generated.pptx

This script POSTs a PDF (base64) to /generate-onepager and saves the PPTX
or saves the server error (JSON or raw) into the output folder.
"""
import argparse
import base64
import json
import sys
from pathlib import Path

import requests


def main():
    p = argparse.ArgumentParser(description="POST a PDF to /generate-onepager and save the PPTX or error.")
    p.add_argument("--pdf", default="backend/data/input/sample.pdf", help="Path to input PDF")
    p.add_argument("--server", default="http://localhost:8000", help="Server base URL")
    p.add_argument("--out", default="backend/data/output/generated.pptx", help="Path to save PPTX on success")
    args = p.parse_args()

    pdf_path = Path(args.pdf)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(2)

    with open(pdf_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    payload = {"file": b64, "filename": pdf_path.name}
    url = args.server.rstrip("/") + "/generate-onepager"

    try:
        resp = requests.post(url, json=payload, timeout=120)
    except Exception as e:
        print("Request failed:", e, file=sys.stderr)
        sys.exit(3)

    print("HTTP", resp.status_code)
    ct = resp.headers.get("content-type", "")
    print("Content-Type:", ct)
    print("Response size:", len(resp.content))

    if resp.status_code == 200 and "presentation" in ct:
        with open(out_path, "wb") as f:
            f.write(resp.content)
        print("Saved PPTX ->", out_path)
        sys.exit(0)
    else:
        # try to save JSON error
        try:
            err = resp.json()
            err_file = out_path.parent / "error.json"
            err_file.write_text(json.dumps(err, indent=2))
            print("Saved error JSON ->", err_file)
        except Exception:
            raw_file = out_path.parent / "error.bin"
            raw_file.write_bytes(resp.content)
            print("Saved raw response ->", raw_file)
        print("Server response body (first 1000 bytes):")
        print(resp.content[:1000])
        sys.exit(1)


if __name__ == "__main__":
    main()
