import pytest
from agents.security_agent.scorer import calculate_risk_score

def test_calculate_risk_score_safe():
    findings = {
        "Prompt Injection": {"attack": "Prompt Injection", "detected": False, "confidence": 0.0, "severity": "Low", "reason": ""}
    }
    assessment = calculate_risk_score(findings)
    assert assessment["risk_score"] == 0
    assert assessment["risk_category"] == "Safe"

def test_calculate_risk_score_critical():
    findings = {
        "Data Exfiltration": {"attack": "Data Exfiltration", "detected": True, "confidence": 1.0, "severity": "High", "reason": "Matched 1 signature(s)", "matched_patterns": ["exfiltrate"]},
        "Prompt Injection": {"attack": "Prompt Injection", "detected": True, "confidence": 1.0, "severity": "High", "reason": "Matched", "matched_patterns": ["ignore"]}
    }
    assessment = calculate_risk_score(findings)
    assert assessment["risk_score"] > 0
    assert assessment["risk_category"] in ["Dangerous", "Critical"]
