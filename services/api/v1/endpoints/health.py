from fastapi import APIRouter
from services.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Liveness probe to check if the application is running."""
    return {
        "status": "healthy",
        "environment": settings.ENV,
        "app_name": settings.APP_NAME
    }

@router.get("/ready")
async def readiness_check():
    """Readiness probe (currently always ready in Phase 1)."""
    return {
        "status": "ready"
    }
