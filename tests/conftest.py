import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    """
    TestClient fixture for FastAPI application.
    """
    with TestClient(app) as test_client:
        yield test_client
