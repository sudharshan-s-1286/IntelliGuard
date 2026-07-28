"""Unit tests for the validator module."""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from privacy_agent.validator import InputValidator, OutputValidator
from privacy_agent.schemas import PrivacyScanRequestSchema, PrivacyScanResponseSchema
from privacy_agent.config import PrivacyAgentConfig
from privacy_agent.exceptions import ValidationError


class TestInputValidator:
    """Tests for InputValidator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = PrivacyAgentConfig()
        self.validator = InputValidator(self.config)

    def test_validate_valid_request(self) -> None:
        """Test validation of a valid request."""
        request = PrivacyScanRequestSchema(text="Hello world")
        self.validator.validate_request(request)

    def test_validate_empty_text(self) -> None:
        """Test that empty text raises ValidationError."""
        request = PrivacyScanRequestSchema(text="   ")
        with pytest.raises(ValidationError):
            self.validator.validate_request(request)

    def test_validate_empty_string(self) -> None:
        """Test that completely empty text raises a validation error."""
        with pytest.raises(PydanticValidationError):
            PrivacyScanRequestSchema(text="")

    def test_validate_large_metadata(self) -> None:
        """Test that large metadata raises ValidationError."""
        large_metadata = {f"key_{i}": f"value_{i}" for i in range(101)}
        request = PrivacyScanRequestSchema(text="Hello", metadata=large_metadata)
        with pytest.raises(ValidationError):
            self.validator.validate_request(request)

    def test_validate_valid_response(self) -> None:
        """Test validation of a valid response."""
        response = PrivacyScanResponseSchema(
            scan_id="scan-123",
            risk_score=10.0,
        )
        self.validator.validate_response(response)

    def test_validate_empty_scan_id(self) -> None:
        """Test that empty scan_id raises ValidationError."""
        response = PrivacyScanResponseSchema(scan_id="")
        with pytest.raises(ValidationError):
            self.validator.validate_response(response)


class TestOutputValidator:
    """Tests for OutputValidator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = PrivacyAgentConfig()
        self.validator = OutputValidator(self.config)

    def test_validate_findings(self) -> None:
        """Test findings validation."""
        findings = [{"severity": "high", "category": "test", "description": "Test"}]
        self.validator.validate_findings(findings)

    def test_validate_findings_missing_severity(self) -> None:
        """Test that findings without severity raise ValidationError."""
        findings = [{"category": "test", "description": "Test"}]
        with pytest.raises(ValidationError):
            self.validator.validate_findings(findings)

    def test_validate_recommendations(self) -> None:
        """Test recommendations validation."""
        recommendations = ["Recommendation 1", "Recommendation 2"]
        self.validator.validate_recommendations(recommendations)

    def test_validate_empty_recommendation(self) -> None:
        """Test that empty recommendation raises ValidationError."""
        recommendations = [""]
        with pytest.raises(ValidationError):
            self.validator.validate_recommendations(recommendations)
