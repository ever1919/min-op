# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage - only copy what we need
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy only necessary application code (exclude .venv, __pycache__, etc.)
COPY api.py .
COPY cv_process_sort_gen.py .
COPY populate_pptx.py .
COPY api/ ./api/
COPY data/ ./data/
COPY prompt_dictionary/ ./prompt_dictionary/

# Clean up to minimize size
RUN find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]