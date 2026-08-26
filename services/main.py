import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from services.core.config import settings
from services.core.logging import setup_logging
from services.api.router import root_router

# Initialize configured logging system
setup_logging()
logger = logging.getLogger("services.main")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="0.1.0"
)

# Register versioned routers under prefix /api
app.include_router(root_router, prefix="/api")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to capture raw stack traces and return a sanitized response."""
    # Log the exception stack trace internally for developers
    logger.error("Unhandled exception: %s at path %s", exc, request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    """Simple root welcome endpoint."""
    return {"message": f"{settings.APP_NAME} is running."}
