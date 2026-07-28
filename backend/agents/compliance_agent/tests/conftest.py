import pytest
from fastapi.testclient import TestClient
from typing import Generator
from app.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Provides a TestClient to make HTTP requests against the FastAPI app."""
    with TestClient(app) as c:
        yield c
