import pytest
from fastapi.testclient import TestClient
from services.main import app

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient instance to test the API endpoints."""
    with TestClient(app) as c:
        yield c
