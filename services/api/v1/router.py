from fastapi import APIRouter
from services.api.v1.endpoints import health, summarize

api_router = APIRouter()

# Include the health router
api_router.include_router(health.router, tags=["health"])

# Include the diff summarization router
api_router.include_router(summarize.router, tags=["diff-summarizer"])
