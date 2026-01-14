FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

# Run with uvicorn; use module path matching files copied into /app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
