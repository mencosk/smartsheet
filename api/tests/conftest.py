import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.upload import _dataframes


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_dataframes():
    """Clear in-memory dataframe store between tests."""
    _dataframes.clear()
    yield
    _dataframes.clear()
