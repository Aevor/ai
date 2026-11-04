"""Integration tests for currently implemented Aevor AI API routes.

These tests verify the shared /v1 route prefix and the implemented
health, readiness, and diff summarization endpoints.

# The eight Platform inference operations are planned separately
and are not covered by these tests.
"""

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


def test_implemented_routes_use_v1_prefix():
    """Verifies the /v1 prefix for currently implemented API routes."""
    client = TestClient(app, base_url="http://localhost:11434")

    health_resp = client.get("/v1/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "healthy"

    ready_resp = client.get("/v1/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "ready"

    mock_service = AsyncMock(spec=DiffSummaryService)
    mock_service.summarize_diff.return_value = PRSummary(
        summary="Diff summarization route verified.",
        key_changes=["Route uses the shared /v1 prefix"],
        review_focus=["services/main.py", "services/core/config.py"]
    )
    app.dependency_overrides[get_diff_summary_service] = lambda: mock_service

    summarize_resp = client.post(
        "/v1/summarize-diff",
        json={"diff": "diff --git a/main.go b/main.go\n+example change"}
    )
    assert summarize_resp.status_code == 200

    data = summarize_resp.json()
    assert data["summary"] == "Diff summarization route verified."
    assert "Route uses the shared /v1 prefix" in data["key_changes"]


def test_configurable_host_and_port(monkeypatch):
    """Verifies that bind host and port are configurable via environment variables."""
    monkeypatch.setenv("AI_SERVICE_HOST", "127.0.0.1")
    monkeypatch.setenv("AI_SERVICE_PORT", "12345")

    custom_settings = Settings()
    assert custom_settings.HOST == "127.0.0.1"
    assert custom_settings.PORT == 12345

    monkeypatch.delenv("AI_SERVICE_HOST")
    monkeypatch.delenv("AI_SERVICE_PORT")
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "11434")

    default_settings = Settings()
    assert default_settings.HOST == "0.0.0.0"
    assert default_settings.PORT == 11434
