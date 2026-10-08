"""Health-check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Return service health status."""
    return {
        "status": "healthy",
        "service": "LandSense AI",
        "version": "1.0.0",
    }
