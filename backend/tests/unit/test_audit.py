import pytest
import os
from agents.security_agent.audit.models import AuditEvent
from agents.security_agent.audit.storage import AuditStorage
from agents.security_agent.audit.analytics import AuditAnalytics
from agents.security_agent.audit.logger import AuditLogger
from agents.security_agent.audit.utils import truncate_string

def test_audit_event_creation():
    event = AuditEvent(
        processing_time_ms=10.0,
        original_prompt="test",
        normalized_prompt="test",
        detected_attacks=[],
        matched_signatures=[],
        risk_score=0,
        confidence=0.0,
        severity="Low",
        risk_category="Safe",
        decision="ALLOW",
        remediation_applied=False,
        safe_prompt="test",
        explanation="test",
        justification=[],
        recommended_action="test"
    )
    assert event.audit_id is not None
    assert event.decision == "ALLOW"

def test_audit_analytics(tmp_path):
    storage_path = str(tmp_path / "test_audit.json")
    storage = AuditStorage(storage_path)
    
    event = AuditEvent(
        processing_time_ms=10.0,
        original_prompt="test",
        normalized_prompt="test",
        detected_attacks=[],
        matched_signatures=[],
        risk_score=0,
        confidence=0.0,
        severity="Low",
        risk_category="Safe",
        decision="ALLOW",
        remediation_applied=False,
        safe_prompt="test",
        explanation="test",
        justification=[],
        recommended_action="test"
    )
    storage.save(event)
    
    analytics = AuditAnalytics(storage)
    assert analytics.total_requests() == 1
    assert analytics.allowed_requests() == 1

def test_truncate_string():
    long_string = "A" * 1000
    truncated = truncate_string(long_string, max_length=100)
    assert len(truncated) == 100 + len("...[TRUNCATED]")
    assert truncated.endswith("...[TRUNCATED]")
