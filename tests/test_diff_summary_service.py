"""Unit tests for the DiffSummaryService service layer."""

import pytest
from unittest.mock import AsyncMock
from models.base import BaseModelProvider
from models.gemini import GeminiConfigError, GeminiResponseError
from models.schemas import PRSummary
from services.diff_summary import (
    DiffEmptyError,
    DiffSizeLimitExceededError,
    DiffSummaryService,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_provider():
    provider = AsyncMock(spec=BaseModelProvider)
    return provider


@pytest.mark.anyio
async def test_service_summarize_success(mock_provider):
    expected_summary = PRSummary(
        summary="Adds health and readiness checks.",
        key_changes=["Implemented /health", "Implemented /ready"],
        review_focus=["services/api/v1/endpoints/health.py"]
    )
    mock_provider.generate_structured.return_value = expected_summary

    service = DiffSummaryService(provider=mock_provider, max_diff_size=5000)
    result = await service.summarize_diff(
        diff="diff --git a/app.py b/app.py\n+def health(): pass",
        title="feat: health endpoints",
        branch="feat/health"
    )

    assert result == expected_summary
    mock_provider.generate_structured.assert_called_once()
    called_kwargs = mock_provider.generate_structured.call_args.kwargs
    assert "diff --git a/app.py b/app.py" in called_kwargs["prompt"]
    assert "feat: health endpoints" in called_kwargs["prompt"]
    assert called_kwargs["response_schema"] == PRSummary


@pytest.mark.anyio
async def test_service_empty_diff_raises(mock_provider):
    service = DiffSummaryService(provider=mock_provider)

    with pytest.raises(DiffEmptyError) as exc_info:
        await service.summarize_diff(diff="")

    assert "Diff content cannot be empty" in str(exc_info.value)
    mock_provider.generate_structured.assert_not_called()


@pytest.mark.anyio
async def test_service_whitespace_diff_raises(mock_provider):
    service = DiffSummaryService(provider=mock_provider)

    with pytest.raises(DiffEmptyError) as exc_info:
        await service.summarize_diff(diff="   \n\t  \n  ")

    assert "Diff content cannot be empty" in str(exc_info.value)
    mock_provider.generate_structured.assert_not_called()


@pytest.mark.anyio
async def test_service_oversized_diff_raises(mock_provider):
    service = DiffSummaryService(provider=mock_provider, max_diff_size=50)

    oversized_diff = "+" * 51
    with pytest.raises(DiffSizeLimitExceededError) as exc_info:
        await service.summarize_diff(diff=oversized_diff)

    assert "exceeds maximum allowed limit of 50 characters" in str(exc_info.value)
    mock_provider.generate_structured.assert_not_called()


@pytest.mark.anyio
async def test_service_propagates_gemini_config_error(mock_provider):
    mock_provider.generate_structured.side_effect = GeminiConfigError("API key missing")

    service = DiffSummaryService(provider=mock_provider)
    with pytest.raises(GeminiConfigError) as exc_info:
        await service.summarize_diff(diff="valid diff")

    assert "API key missing" in str(exc_info.value)


@pytest.mark.anyio
async def test_service_propagates_gemini_response_error(mock_provider):
    mock_provider.generate_structured.side_effect = GeminiResponseError("Upstream failure")

    service = DiffSummaryService(provider=mock_provider)
    with pytest.raises(GeminiResponseError) as exc_info:
        await service.summarize_diff(diff="valid diff")

    assert "Upstream failure" in str(exc_info.value)
