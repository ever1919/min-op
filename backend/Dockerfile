# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Test stage (dev/CI only) ---
# This stage keeps tests out of the production image, while allowing docker-compose
# to run pytest in a dedicated service that can gate backend/frontend startup.
FROM python:3.11-slim AS test

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

COPY --from=builder /root/.local /root/.local

# Copy the same runtime code as the final image
COPY api.py .
COPY cv_process_sort_gen.py .
COPY populate_pptx.py .
COPY api/ ./api/
COPY data/ ./data/
COPY prompt_dictionary/ ./prompt_dictionary/

# Copy tests ONLY into this stage
# (expected layout: tests/ + conftest.py)
COPY tests/ ./tests/

# Default command for the test image: run pytest and print total duration.
# - If tests fail, container exits non-zero and docker-compose will show the failure.
CMD ["python", "-c", "import subprocess,sys,time; t0=time.perf_counter(); rc=subprocess.call(['pytest','-q','--durations=20','--durations-min=0.05']); dt=time.perf_counter()-t0; print(f'TEST_TOTAL_SECONDS={dt:.2f}'); sys.exit(rc)"]

# Final stage - minimal base image
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Copy only installed packages from builder (not build tools)
COPY --from=builder /root/.local /root/.local

# Copy only necessary application code
COPY api.py .
COPY cv_process_sort_gen.py .
COPY populate_pptx.py .
COPY api/ ./api/
COPY data/ ./data/
COPY prompt_dictionary/ ./prompt_dictionary/

# Remove unnecessary files and clean up
RUN find /root/.local -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type f -name "*.pyc" -delete && \
    find /root/.local -type f -name "*.pyo" -delete && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
