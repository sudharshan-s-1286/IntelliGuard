import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_privacy_health_endpoint():
    response = client.get("/api/v1/privacy/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_privacy_analyze_endpoint():
    response = client.post("/api/v1/privacy/analyze", json={"text": "Hello world"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["agent"] == "PrivacyAgent"
    assert "risk_score" in data
    assert "risk_level" in data

def test_privacy_analyze_endpoint_empty():
    response = client.post("/api/v1/privacy/analyze", json={"text": ""})
    assert response.status_code == 400

def test_privacy_analyze_endpoint_malformed():
    response = client.post("/api/v1/privacy/analyze", json={"not_text": "Hello"})
    assert response.status_code == 422
