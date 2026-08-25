from fastapi import APIRouter
from services.api.v1.router import api_router as v1_router

root_router = APIRouter()

# Include v1 router under prefix /v1
root_router.include_router(v1_router, prefix="/v1")
