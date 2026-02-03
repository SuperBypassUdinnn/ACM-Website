"""
Health Check Routes

Status and health monitoring endpoints.
"""

from fastapi import APIRouter
from backend.database import get_db_pool

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint"""
    db_status = "connected" if get_db_pool() else "disconnected"
    return {"status": "ok", "database": db_status}


@router.get("/")
async def root():
    """API root endpoint"""
    return {"message": "ACM AI Chatbot API", "version": "2.0"}
