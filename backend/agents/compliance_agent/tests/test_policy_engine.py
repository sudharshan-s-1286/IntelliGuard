import os
import tempfile
import yaml
import pytest
from agents.compliance_agent.decision import PolicyEngine

@pytest.fixture
def mock_config():
    rules = {
        "rules": [
            {
                "id": "001",
                "role": "guest",
                "contains": "confidential",
                "severity": "HIGH"
            },
            {
                "id": "002",
                "contains": "diagnosis",
                "severity": "CRITICAL"
            },
            {
                "id": "003",
                "role": "user",
                "contains": "password",
                "severity": "MEDIUM"
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        yaml.dump(rules, f)
        temp_path = f.name
        
    yield temp_path
    
    os.remove(temp_path)

@pytest.fixture
def engine(mock_config):
    return PolicyEngine(config_path=mock_config)

def test_engine_loads_rules(engine):
    assert len(engine.rules) == 3
    assert engine.rules[0]["id"] == "001"

def test_evaluate_rule_001(engine):
    # Rule 001: role=guest, contains=confidential
    context = {"role": "guest"}
    findings = ["This is a CONFIDENTIAL document"]
    
    violations = engine.evaluate(context, findings)
    
    assert len(violations) == 1
    assert violations[0]["id"] == "001"
    assert violations[0]["severity"] == "HIGH"

def test_evaluate_rule_001_wrong_role(engine):
    # Should not violate if role is different
    context = {"role": "admin"}
    findings = ["This is a CONFIDENTIAL document"]
    
    violations = engine.evaluate(context, findings)
    
    assert len(violations) == 0

def test_evaluate_rule_002_no_context_needed(engine):
    # Rule 002: contains=diagnosis, no role specified
    context = {"role": "guest"} # Role shouldn't matter
    findings = ["Patient diagnosis is flu"]
    
    violations = engine.evaluate(context, findings)
    
    assert len(violations) == 1
    assert violations[0]["id"] == "002"
    assert violations[0]["severity"] == "CRITICAL"

def test_evaluate_multiple_violations(engine):
    context = {"role": "guest"}
    findings = ["CONFIDENTIAL patient diagnosis details"]
    
    violations = engine.evaluate(context, findings)
    
    assert len(violations) == 2
    ids = [v["id"] for v in violations]
    assert "001" in ids
    assert "002" in ids

def test_no_violations(engine):
    context = {"role": "user"}
    findings = ["Nothing to see here"]
    
    violations = engine.evaluate(context, findings)
    
    assert len(violations) == 0
