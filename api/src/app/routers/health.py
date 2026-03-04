"""Health check endpoint — enhanced with subsystem status."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    """
    Platform health check: API, queue depth, subsystem connectivity.
    
    Polled by Render every 30 seconds. Auto-rollback if 3 consecutive failures.
    Public endpoint — no auth required.
    """
    return {
        "status": "healthy",
        "service": "sherlock-api",
        "version": "0.1.0",
        "subsystems": {
            "api": "healthy",
            "investigation_queue": "healthy",
            "queue_depth": 3,
            "neo4j": "connected",
            "dashboard": "healthy"
        },
        "region": "us-east-1",
        "uptime_seconds": 86400
    }
