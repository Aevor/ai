from unittest.mock import patch

def test_root_endpoint(client):
    """Tests the base API root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"]

def test_health_endpoint(client):
    """Tests that GET /api/v1/health returns a healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "app_name" in data

def test_ready_endpoint(client):
    """Tests that GET /api/v1/ready returns a ready status."""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

def test_global_exception_handler():
    """Tests that unhandled exceptions return a sanitized 500 error response."""
    from fastapi.testclient import TestClient
    from services.main import app

    @app.get("/api/v1/crash-test")
    async def crash_test():
        raise ValueError("Simulated critical error")

    # Disable raising exceptions in TestClient to let exception handler intercept
    custom_client = TestClient(app, raise_server_exceptions=False)
    response = custom_client.get("/api/v1/crash-test")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


