"""Integration tests for the Privacy Agent."""

from __future__ import annotations

import json
import time

import pytest

from privacy_agent import PrivacyAgent
from privacy_agent.config import PrivacyAgentConfig


class TestPrivacyAgentIntegration:
    """Integration tests for PrivacyAgent with Orchestrator contract."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.agent = PrivacyAgent()

    def test_basic_orchestrator_contract(self) -> None:
        """Test basic Orchestrator contract compliance."""
        context = {
            "request_id": "integration-test",
            "text": "Contact alice@example.com or call 555-123-4567",
            "metadata": {"source": "orchestrator"},
        }
        response = self.agent.run(context)

        assert response["status"] == "success"
        assert response["agent"] == "PrivacyAgent"
        assert response["request_id"] == "integration-test"
        assert isinstance(response["risk_score"], float)
        assert 0.0 <= response["risk_score"] <= 100.0
        assert response["risk_level"] in {
            "low", "medium", "high", "critical"
        }
        assert isinstance(response["findings"], list)
        assert isinstance(response["recommendations"], list)
        assert response["metadata"] == {"source": "orchestrator"}
        assert response["errors"] == []

    def test_response_is_json_serializable(self) -> None:
        """Test that the response can be serialized to JSON."""
        context = {
            "request_id": "json-test",
            "text": "Email user@example.com and SSN 123-45-6789",
        }
        response = self.agent.run(context)
        serialized = json.dumps(response)
        assert isinstance(serialized, str)
        assert len(serialized) > 0

    def test_empty_text_returns_error(self) -> None:
        """Test that empty text returns error status."""
        context = {
            "request_id": "empty-text",
            "text": "",
        }
        response = self.agent.run(context)
        assert response["status"] == "error"
        assert len(response["errors"]) > 0
        assert response["risk_score"] == 0.0

    def test_extremely_large_text(self) -> None:
        """Test handling of extremely large text."""
        large_text = "Email test@example.com. " * 5000
        context = {
            "request_id": "large-text",
            "text": large_text,
        }
        start = time.perf_counter()
        response = self.agent.run(context)
        elapsed = time.perf_counter() - start

        assert response["status"] == "success"
        assert elapsed < 30.0

    def test_unicode_text(self) -> None:
        """Test handling of Unicode text."""
        context = {
            "request_id": "unicode-test",
            "text": "Email ñoño@example.com 日本 123-45-6789 🎉",
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
        assert isinstance(response["findings"], list)

    def test_multiple_emails(self) -> None:
        """Test detection of multiple email addresses."""
        context = {
            "request_id": "multi-email",
            "text": "a@b.com c@d.com e@f.org",
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
        assert response["risk_score"] > 0.0

    def test_mixed_pii(self) -> None:
        """Test detection of mixed PII types."""
        context = {
            "request_id": "mixed-pii",
            "text": (
                "Email: alice@example.com "
                "Phone: 555-123-4567 "
                "SSN: 123-45-6789 "
                "Card: 4111-1111-1111-1111"
            ),
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
        assert response["risk_score"] > 0.0
        assert len(response["findings"]) > 0

    def test_invalid_input_missing_text(self) -> None:
        """Test handling of invalid input without text field."""
        context = {
            "request_id": "invalid-input",
            "metadata": {},
        }
        response = self.agent.run(context)
        assert response["status"] == "error"
        assert len(response["errors"]) > 0

    def test_null_values(self) -> None:
        """Test handling of null values in input."""
        context = {
            "request_id": "null-test",
            "text": None,
        }
        response = self.agent.run(context)
        assert response["status"] == "error"

    def test_no_findings_clean_text(self) -> None:
        """Test that clean text produces no findings."""
        context = {
            "request_id": "no-findings",
            "text": "This is a completely clean sentence with no PII.",
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
        assert response["risk_score"] == 0.0
        assert len(response["findings"]) == 1
        assert response["findings"][0]["severity"] == "info"

    def test_all_supported_entity_types(self) -> None:
        """Test detection of all supported PII entity types."""
        text = (
            "Email: user@example.com "
            "Phone: (555) 123-4567 "
            "SSN: 123-45-6789 "
            "Card: 4111-1111-1111-1111 "
            "IP: 192.168.1.1 "
            "DOB: 01/15/1990 "
            "MR: Medical Record #12345"
        )
        context = {
            "request_id": "all-types",
            "text": text,
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
        assert len(response["findings"]) > 0

    def test_duplicate_entities(self) -> None:
        """Test handling of duplicate PII values."""
        context = {
            "request_id": "duplicate",
            "text": "Email test@test.com and also test@test.com again",
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
        assert response["risk_score"] > 0.0

    def test_risk_level_mapping(self) -> None:
        """Test risk level mapping for different score ranges."""
        agent = PrivacyAgent(config=PrivacyAgentConfig(risk_score_cap=100.0))

        low_text = "Email a@b.com"
        low_response = agent.run({
            "request_id": "risk-low",
            "text": low_text,
        })
        assert low_response["risk_level"] in {"low", "medium"}

    def test_metadata_passthrough(self) -> None:
        """Test that metadata is passed through unchanged."""
        metadata = {"source": "api", "user_id": "123", "tags": ["pii", "test"]}
        context = {
            "request_id": "meta-passthrough",
            "text": "Email test@example.com",
            "metadata": metadata,
        }
        response = self.agent.run(context)
        assert response["metadata"] == metadata

    def test_multiple_aadhaar_handled_gracefully(self) -> None:
        """Test that text containing Aadhaar numbers is handled gracefully."""
        context = {
            "request_id": "aadhaar-test",
            "text": "Aadhaar: 123412341234 and 567856785678",
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
        assert isinstance(response["risk_score"], float)

    def test_multiple_pan_not_detected(self) -> None:
        """Test that PAN numbers are not detected (not a supported type)."""
        context = {
            "request_id": "pan-test",
            "text": "PAN: ABCDE1234F and PQRST5678G",
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
        assert response["risk_score"] == 0.0

    def test_very_long_document(self) -> None:
        """Test processing of a very long document."""
        long_text = (
            "Email user@example.com. " * 1000
            + "SSN 123-45-6789. " * 100
        )
        context = {
            "request_id": "long-doc",
            "text": long_text,
        }
        start = time.perf_counter()
        response = self.agent.run(context)
        elapsed = time.perf_counter() - start

        assert response["status"] == "success"
        assert elapsed < 60.0

    def test_special_characters_in_text(self) -> None:
        """Test handling of special characters."""
        context = {
            "request_id": "special-chars",
            "text": "Email: user@example.com <script>alert('xss')</script>",
        }
        response = self.agent.run(context)
        assert response["status"] == "success"
