"""API endpoint for Git diff summarization."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from models.gemini import GeminiConfigError, GeminiResponseError
from models.schemas import DiffSummaryRequest, PRSummary
from services.diff_summary import (
    DiffEmptyError,
    DiffSizeLimitExceededError,
    DiffSummaryService,
)

logger = logging.getLogger("services.api.v1.endpoints.summarize")

router = APIRouter()


def get_diff_summary_service() -> DiffSummaryService:
    """Dependency provider returning an instance of DiffSummaryService."""
    return DiffSummaryService()


@router.post(
    "/summarize-diff",
    response_model=PRSummary,
    status_code=status.HTTP_200_OK,
    summary="Generate a structured pull request summary from a Git diff",
    description=(
        "Accepts a unified Git diff and optional metadata, validates the input, "
        "and uses the AI provider to generate a structured PR summary including "
        "overview, key changes, and review focus areas."
    ),
)
async def summarize_diff_endpoint(
    request: DiffSummaryRequest,
    service: DiffSummaryService = Depends(get_diff_summary_service),
) -> PRSummary:
    """Endpoint handler for diff summarization."""
    logger.info("Received summarize-diff request (diff characters: %d)", len(request.diff))
    try:
        summary = await service.summarize_diff(
            diff=request.diff,
            title=request.title,
            description=request.description,
            branch=request.branch,
        )
        return summary
    except DiffEmptyError as err:
        logger.warning("Diff summarization rejected: empty diff")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Diff content cannot be empty.",
        ) from err
    except DiffSizeLimitExceededError as err:
        logger.warning("Diff summarization rejected: oversized diff (%d characters)", len(request.diff))
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(err),
        ) from err
    except GeminiConfigError as err:
        logger.error("Diff summarization failed: provider configuration missing")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI model provider is not configured.",
        ) from err
    except GeminiResponseError as err:
        logger.error("Diff summarization failed: upstream provider error")
        err_msg = str(err)
        if "validation against schema" in err_msg or "Invalid Gemini response structure" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to parse structured summary from AI provider.",
            ) from err
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upstream AI model provider request failed.",
        ) from err
