import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_compliance_check_clean():
    payload = {
        "text": "This is a clean, standard document with no sensitive info."
    }
    response = client.post("/api/compliance/check", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Compliant"
    assert data["decision"] == "ALLOW"
    assert data["score"] == 0
    assert len(data["violations"]) == 0

def test_compliance_check_violations():
    payload = {
        "text": "My AWS access key is AKIAFAKE123456789012 and my email is hacker@evil.com"
    }
    response = client.post("/api/compliance/check", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Non-Compliant"
    assert data["decision"] in ["REVIEW", "BLOCK"]
    assert data["score"] > 0
    assert len(data["violations"]) >= 1
    assert len(data["recommendations"]) >= 1

def test_compliance_check_validation_error():
    # Sending missing text should raise 422
    payload = {}
    response = client.post("/api/compliance/check", json=payload)
    
    assert response.status_code == 422
    assert "detail" in response.json()
