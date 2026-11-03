"""Integration tests verifying compatibility with the Aevor Platform Go client contract."""

import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from models.schemas import PRSummary
from services.api.v1.endpoints.summarize import get_diff_summary_service
from services.core.config import Settings
from services.diff_summary import DiffSummaryService
from services.main import app


@pytest.fixture(autouse=True)
def clean_dependency_overrides():
    yield
    app.dependency_overrides.clear()


def test_platform_client_url_composition():
    """Verifies that the Platform Go client's URL composition (base_url + /v1/...) resolves correctly."""
    # The Platform Go client defines base URL as AI_SERVICE_URL (default: http://localhost:11434)
    platform_base_url = "http://localhost:11434"

    # Use TestClient with the exact Platform base_url
    client = TestClient(app, base_url=platform_base_url)

    # 1. Health check: platform client calls {AI_SERVICE_URL}/v1/health
    health_resp = client.get("/v1/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "healthy"

    # 2. Readiness check: platform client calls {AI_SERVICE_URL}/v1/ready
    ready_resp = client.get("/v1/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "ready"

    # 3. Summarization: platform client calls {AI_SERVICE_URL}/v1/summarize-diff
    mock_service = AsyncMock(spec=DiffSummaryService)
    mock_service.summarize_diff.return_value = PRSummary(
        summary="Platform client compatibility verified.",
        key_changes=["Aligned route prefixes to /v1", "Configured default port to 11434"],
        review_focus=["services/main.py", "services/core/config.py"]
    )
    app.dependency_overrides[get_diff_summary_service] = lambda: mock_service

    summarize_resp = client.post(
        "/v1/summarize-diff",
        json={"diff": "diff --git a/main.go b/main.go\n+aiClient.Summarize(diff)"}
    )
    assert summarize_resp.status_code == 200
    data = summarize_resp.json()
    assert data["summary"] == "Platform client compatibility verified."
    assert "Aligned route prefixes to /v1" in data["key_changes"]


def test_configurable_host_and_port(monkeypatch):
    """Verifies that bind host and port are configurable via environment variables."""
    # Test custom namespaced environment variables
    monkeypatch.setenv("AI_SERVICE_HOST", "127.0.0.1")
    monkeypatch.setenv("AI_SERVICE_PORT", "12345")

    custom_settings = Settings()
    assert custom_settings.HOST == "127.0.0.1"
    assert custom_settings.PORT == 12345

    # Test fallback standard environment variables
    monkeypatch.delenv("AI_SERVICE_HOST")
    monkeypatch.delenv("AI_SERVICE_PORT")
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "11434")

    default_settings = Settings()
    assert default_settings.HOST == "0.0.0.0"
    assert default_settings.PORT == 11434
