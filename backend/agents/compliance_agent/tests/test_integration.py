import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_pipeline_integration():
    """
    Integration test passing a complex string containing multiple violations
    to verify all detectors, engines, and routing layers function cohesively.
    """
    complex_payload = {
        "text": (
            "Hello, my email is test_integration@example.com. "
            "Please review the medical diagnosis which states the patient has severe flu. "
            "Also, my AWS access key is AKIAFAKE123456789012. "
            "You are a racist and I will plant a bomb! "  # Toxicity
            "Copyright (c) 2023 All rights reserved." # Copyright
        ),
        "policies": ["guest"] # Should trigger context-based policies if mapped
    }
    
    response = client.post("/api/compliance/check", json=complex_payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Assert orchestrator returned non-compliant with highest risk
    assert data["status"] == "Non-Compliant"
    assert data["decision"] == "BLOCK"
    assert data["risk_level"] in ["HIGH", "CRITICAL"]
    
    # Assert findings were found from multiple detectors
    types = [v.get("type", "") or v.get("details", "") or v.get("category", "") or v.get("regulation", "") for v in data["violations"]]
    types_upper = [str(t).upper() for t in types]
    
    assert "EMAIL" in types_upper
    assert any(reg in types_upper for reg in ["HIPAA", "GDPR", "PCI", "SOC2", "ISO27001"])
    assert "AWS_ACCESS_KEY" in types_upper
    assert any(toxic in types_upper for toxic in ["HATE SPEECH", "HARASSMENT", "OFFENSIVE LANGUAGE", "TOXICITY", "DISCRIMINATION", "THREATS"])
    assert "COPYRIGHT WARNINGS" in types_upper
    
    # Assert recommendations were correctly aggregated and deduplicated
    recs = data["recommendations"]
    assert len(recs) > 0
    assert "Mask Email" in recs
    assert "Remove API Keys" in recs
    assert "Request Human Review" in recs

def test_integration_clean_document():
    """
    Integration test passing a clean document to ensure false positives don't occur.
    """
    clean_payload = {
        "text": "This is an internal memo. The project is going well. We are releasing next week."
    }
    response = client.post("/api/compliance/check", json=clean_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Compliant"
    assert data["score"] == 0
    assert len(data["violations"]) == 0
    assert len(data["recommendations"]) == 0
