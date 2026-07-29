import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_health_endpoint():
    response = client.get("/api/security/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_analyze_endpoint_safe():
    response = client.post("/api/security/analyze", json={"prompt": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["result"]["decision"] == "ALLOW"

@pytest.mark.asyncio
async def test_analyze_endpoint_empty():
    response = client.post("/api/security/analyze", json={"prompt": ""})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_analyze_endpoint_malformed():
    response = client.post("/api/security/analyze", json={"not_prompt": "Hello"})
    assert response.status_code == 422
