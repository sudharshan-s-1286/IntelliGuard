"""Unit tests for the PrivacyAgent entry point."""

from __future__ import annotations

import pytest

from privacy_agent.agent import PrivacyAgent
from privacy_agent.config import PrivacyAgentConfig


class TestPrivacyAgent:
    """Tests for the PrivacyAgent class."""

    def test_init_with_default_config(self) -> None:
        """Test initialization with default configuration."""
        agent = PrivacyAgent()
        assert agent._config is not None

    def test_init_with_custom_config(self) -> None:
        """Test initialization with custom configuration."""
        config = PrivacyAgentConfig(confidence_threshold=0.8)
        agent = PrivacyAgent(config=config)
        assert agent._config.confidence_threshold == 0.8

    def test_run_returns_dict(self) -> None:
        """Test that run returns a dictionary."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-1",
            "text": "Contact user at test@example.com",
        })
        assert isinstance(result, dict)

    def test_run_detects_entities(self) -> None:
        """Test that run detects PII entities."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-2",
            "text": "Email alice@example.com",
        })
        assert result["status"] == "success"
        assert len(result["findings"]) > 0

    def test_run_includes_risk_score(self) -> None:
        """Test that risk_score is in the result."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-3",
            "text": "Email user@example.com",
        })
        assert "risk_score" in result
        assert isinstance(result["risk_score"], float)
        assert 0.0 <= result["risk_score"] <= 100.0

    def test_run_includes_findings(self) -> None:
        """Test that findings are in the result."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-4",
            "text": "SSN 123-45-6789",
        })
        assert "findings" in result
        assert isinstance(result["findings"], list)

    def test_run_includes_recommendations(self) -> None:
        """Test that recommendations are in the result."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-5",
            "text": "SSN 123-45-6789",
        })
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    def test_run_includes_agent_name(self) -> None:
        """Test that agent name is PrivacyAgent."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-6",
            "text": "Hello world",
        })
        assert result["agent"] == "PrivacyAgent"

    def test_run_includes_request_id(self) -> None:
        """Test that request_id is passed through."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "integration-test",
            "text": "Hello world",
        })
        assert result["request_id"] == "integration-test"

    def test_run_includes_risk_level(self) -> None:
        """Test that risk_level is present and valid."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-7",
            "text": "Hello world",
        })
        assert "risk_level" in result
        assert result["risk_level"] in {
            "low", "medium", "high", "critical"
        }

    def test_run_with_metadata(self) -> None:
        """Test run with metadata."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-8",
            "text": "Email test@test.com",
            "metadata": {"source": "test"},
        })
        assert result["metadata"] == {"source": "test"}

    def test_run_clean_text(self) -> None:
        """Test run with text containing no PII."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-9",
            "text": "This is a clean sentence.",
        })
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["risk_score"] == 0.0

    def test_run_with_empty_text_returns_error(self) -> None:
        """Test that empty text returns error status, not exception."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-10",
            "text": "",
        })
        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_run_generates_request_id_when_missing(self) -> None:
        """Test that missing request_id is handled gracefully."""
        agent = PrivacyAgent()
        result = agent.run({
            "text": "Hello world",
        })
        assert "request_id" in result

    def test_run_success_has_no_errors(self) -> None:
        """Test that successful response has empty errors list."""
        agent = PrivacyAgent()
        result = agent.run({
            "request_id": "test-11",
            "text": "Hello world",
        })
        assert result["status"] == "success"
        assert result["errors"] == []
