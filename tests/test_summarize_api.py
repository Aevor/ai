"""API integration unit tests for POST /summarize-diff endpoint."""

import logging
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from models.gemini import GeminiConfigError, GeminiResponseError
from models.schemas import PRSummary
from services.api.v1.endpoints.summarize import get_diff_summary_service
from services.core.config import settings
from services.diff_summary import DiffSummaryService
from services.main import app


@pytest.fixture(autouse=True)
def clean_dependency_overrides():
    """Ensure dependency overrides are cleared after each test."""
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_summary_result():
    return PRSummary(
        summary="Refactored database pool configuration.",
        key_changes=["Replaced static pool with dynamic pool", "Added connection timeout"],
        review_focus=["services/core/db.py"]
    )


def test_summarize_diff_api_success(mock_summary_result):
    """Verifies that canonical /v1/summarize-diff succeeds with a valid diff payload."""
    mock_service = AsyncMock(spec=DiffSummaryService)
    mock_service.summarize_diff.return_value = mock_summary_result

    app.dependency_overrides[get_diff_summary_service] = lambda: mock_service
    client = TestClient(app)

    payload = {
        "diff": "diff --git a/file.py b/file.py\n+print('test')",
        "title": "feat: test",
        "description": "test pr",
        "branch": "feat/test"
    }

    # Test canonical /v1/summarize-diff
    response = client.post("/v1/summarize-diff", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == mock_summary_result.summary
    assert data["key_changes"] == mock_summary_result.key_changes
    assert data["review_focus"] == mock_summary_result.review_focus


def test_summarize_diff_empty_diff_returns_400():
    """Verifies that an empty diff string returns 400 Bad Request."""
    client = TestClient(app)
    response = client.post("/v1/summarize-diff", json={"diff": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Diff content cannot be empty."


def test_summarize_diff_whitespace_diff_returns_400():
    """Verifies that whitespace-only diff returns 400 Bad Request."""
    client = TestClient(app)
    response = client.post("/v1/summarize-diff", json={"diff": "   \n\t  "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Diff content cannot be empty."


def test_summarize_diff_oversized_diff_returns_413():
    """Verifies that oversized diff returns 413 Request Entity Too Large."""
    client = TestClient(app)
    oversized = "+" * (settings.MAX_DIFF_SIZE_CHARS + 10)
    response = client.post("/v1/summarize-diff", json={"diff": oversized})
    assert response.status_code == 413
    assert "exceeds maximum allowed limit" in response.json()["detail"]


def test_summarize_diff_missing_diff_field_returns_422():
    """Verifies that requests missing the required diff field return 422 Unprocessable Entity."""
    client = TestClient(app)
    response = client.post("/v1/summarize-diff", json={"title": "No diff here"})
    assert response.status_code == 422


def test_summarize_diff_missing_gemini_config_returns_503():
    """Verifies that missing Gemini API key returns 503 Service Unavailable."""
    mock_service = AsyncMock(spec=DiffSummaryService)
    mock_service.summarize_diff.side_effect = GeminiConfigError("Gemini API key is not configured.")

    app.dependency_overrides[get_diff_summary_service] = lambda: mock_service
    client = TestClient(app)
    response = client.post("/v1/summarize-diff", json={"diff": "diff --git a b"})
    assert response.status_code == 503
    assert response.json()["detail"] == "AI model provider is not configured."


def test_summarize_diff_upstream_provider_failure_returns_502():
    """Verifies that upstream HTTP failure from provider returns 502 Bad Gateway."""
    mock_service = AsyncMock(spec=DiffSummaryService)
    mock_service.summarize_diff.side_effect = GeminiResponseError("Gemini API call failed with status code 500")

    app.dependency_overrides[get_diff_summary_service] = lambda: mock_service
    client = TestClient(app)
    response = client.post("/v1/summarize-diff", json={"diff": "diff --git a b"})
    assert response.status_code == 502
    assert response.json()["detail"] == "Upstream AI model provider request failed."


def test_summarize_diff_invalid_model_output_returns_502():
    """Verifies that malformed model response / validation failure returns 502 Bad Gateway."""
    mock_service = AsyncMock(spec=DiffSummaryService)
    mock_service.summarize_diff.side_effect = GeminiResponseError("Generated content failed validation against schema: invalid")

    app.dependency_overrides[get_diff_summary_service] = lambda: mock_service
    client = TestClient(app)
    response = client.post("/v1/summarize-diff", json={"diff": "diff --git a b"})
    assert response.status_code == 502
    assert response.json()["detail"] == "Failed to parse structured summary from AI provider."


def test_logging_does_not_leak_diff_or_api_key_or_response_body(caplog):
    """Verifies that raw diff text, API keys, and provider responses are never written to logs."""
    secret_key = "super-secret-api-key-12345"
    confidential_code = "CONFIDENTIAL_ALGORITHM_SOURCE_CODE_ABCXYZ"
    diff_content = f"diff --git a/core.py b/core.py\n+{confidential_code}\n+token='{secret_key}'"
    raw_provider_body = '{"raw_provider_internal_trace": "should_not_leak"}'

    mock_provider = AsyncMock()
    mock_provider.generate_structured.side_effect = GeminiResponseError(
        f"API call failed with status code 500: {raw_provider_body}"
    )

    service = DiffSummaryService(provider=mock_provider)
    app.dependency_overrides[get_diff_summary_service] = lambda: service

    with caplog.at_level(logging.DEBUG):
        client = TestClient(app)
        response = client.post("/v1/summarize-diff", json={"diff": diff_content})

        assert response.status_code == 502

        logged_text = caplog.text

        # Assert no sensitive content is in logs
        assert confidential_code not in logged_text
        assert secret_key not in logged_text
        assert raw_provider_body not in logged_text
