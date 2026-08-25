from fastapi import APIRouter
from services.api.v1.endpoints import health

api_router = APIRouter()

# Include the health router
api_router.include_router(health.router, tags=["health"])
