# AGENTS.md - Development Guidelines for CV One-Pager Generator

## Project Overview
We're building a web app as an internal tool to automate the resume creation process. The app should be simple, minimalistic and easy to use, but not ugly or simplistic. Strike the best mix of modern design with minimalist code. Less code is always best code - try to find the simplest way to make changes.

**Tech Stack:**
- Backend: Python with FastAPI
- Frontend: React with Tailwind CSS
- Infrastructure: Docker Compose
- AI: OpenAI API for CV processing

## Development Commands

### Backend (Python FastAPI)
```bash
# Development server (from backend directory)
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Install dependencies (traditional pip)
pip install -r requirements.txt

# Install dependencies (UV - recommended faster alternative)
uv pip install -r requirements.txt

# Run specific test
python -m pytest tests/test_generate.py -v

# Run all tests
python -m pytest tests/ -v

# Docker build and run (now uses optimized multi-stage build)
docker build -t backend .
docker run -p 8000:8000 backend
```

### Frontend (React)
```bash
# Development server (from frontend directory)
npm start

# Build for production
npm run build

# Run tests
npm test

# Run specific test
npm test -- --testNamePattern="specific test name"

# Install dependencies
npm install
```

### Full Stack (Docker Compose)
```bash
# Start both services
docker-compose up

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

## Code Style Guidelines

### Python (Backend)
**Imports:**
- Standard library imports first, then third-party, then local
- Use `from pathlib import Path` for file operations
- Group related imports together

```python
# Standard library
import os
import json
from pathlib import Path
from typing import Optional

# Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

# Local imports
import cv_process_sort_gen as gen
import populate_pptx as pptx
```

**Type Hints:**
- Always use type hints for function parameters and return values
- Use Optional for nullable parameters
- Use Pydantic models for API request/response

**Naming Conventions:**
- Functions: snake_case (e.g., `extract_text_from_pdf`)
- Variables: snake_case (e.g., `coe_selected`)
- Classes: PascalCase (e.g., `GenerateRequest`)
- Constants: UPPER_SNAKE_CASE

**Error Handling:**
- Use HTTPException for API errors with appropriate status codes
- Log errors with descriptive messages
- Use try/except blocks for external API calls and file operations

**File Organization:**
- Main API file: `api.py`
- Processing modules: descriptive names (e.g., `cv_process_sort_gen.py`)
- Use relative imports within the backend package
- Handle paths with `BASE_DIR = Path(__file__).resolve().parent`

### React/Frontend (JSX)
**Component Structure:**
- Use functional components with hooks
- Export default as the main component
- Keep components focused and single-purpose

```jsx
import React, { useState, useEffect } from 'react';
import { Upload, FileText } from 'lucide-react';

export default function CVOnePagerGenerator() {
  // Component logic
  return (
    // JSX with Tailwind classes
  );
}
```

**Styling:**
- Use Tailwind CSS classes directly in JSX
- Avoid separate CSS files when possible
- Follow responsive design patterns with Tailwind breakpoints
- Use consistent color scheme (purple-600 for primary actions)

**State Management:**
- Use useState for local component state
- Use useEffect for side effects and API calls
- Keep state variables descriptive (e.g., `isProcessing`, `uploadedFile`)

**File Handling:**
- Convert files to base64 for API transmission
- Validate file types and sizes before upload
- Use FileReader API for client-side file processing

### API Design (FastAPI)
**Endpoints:**
- Use descriptive endpoint names (e.g., `/generate-onepager`)
- Use GET for data retrieval, POST for creation/generation
- Return appropriate HTTP status codes

**Request/Response:**
- Use Pydantic models for request validation
- Return StreamingResponse for file downloads
- Include proper error messages in HTTPException

**CORS:**
- Configure CORS for local development
- Use specific origins in production

## Testing Guidelines

### Backend Tests
- Test files in `backend/tests/` directory
- Use pytest for testing framework
- Test API endpoints with sample data
- Mock external API calls (OpenAI) when possible

### Frontend Tests
- Use React Testing Library
- Test user interactions and state changes
- Test file upload and form validation
- Mock API calls in component tests

### Running Single Tests
```bash
# Backend specific test
python -m pytest tests/test_generate.py::test_function_name -v

# Frontend specific test
npm test -- --testNamePattern="specific test name"
```

## Development Workflow

### Environment Setup
1. Clone repository and navigate to project root
2. Backend: `cd backend && pip install -r requirements.txt`
3. Frontend: `cd frontend && npm install`
4. Set up environment variables (see `.env.example`)

### Docker Development
- Use Docker Compose for full-stack development
- Mount volumes for live code changes
- Use `--build` flag when dependencies change

### Code Review Principles
- Keep changes minimal and focused
- Follow existing code patterns and conventions
- Ensure all tests pass before submitting
- Test both frontend and backend integration

## Security & Best Practices

### API Keys
- Store OpenAI API key in environment variables
- Never commit API keys to repository
- Use `.env` files for local development

### File Upload Security
- Validate file types (PDF only)
- Limit file sizes (200MB max)
- Clean up temporary files after processing

### Error Handling
- Never expose sensitive information in error messages
- Log errors appropriately for debugging
- Provide user-friendly error messages

### Performance
- Use streaming for file downloads
- Clean up temporary files and resources
- Optimize API response times

## Project Structure Notes

### Backend Organization
- `api.py`: Main FastAPI application
- `cv_process_sort_gen.py`: CV text processing
- `populate_pptx.py`: PowerPoint generation
- `data/input/` and `data/output/`: File storage
- `prompt_dictionary/`: OpenAI prompt templates

### Frontend Organization
- `src/App.jsx`: Main application component
- Use Tailwind CSS for all styling
- Lucide React for icons
- Single-page application architecture

### Important Patterns
- Backend uses relative path handling with `BASE_DIR`
- Frontend uses controlled components with React state
- API communication uses JSON with base64 file encoding
- Error handling is consistent across frontend and backend