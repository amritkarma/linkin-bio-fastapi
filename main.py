"""
FastAPI Application Entry Point

Run with: uvicorn main:app --reload
From the fastapi-linkin-bio directory.
"""
from app.main import app

__all__ = ["app"]
