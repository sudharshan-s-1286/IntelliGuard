"""Validation module for the Privacy Agent."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from .schemas import (
    PrivacyScanRequestSchema,
    PrivacyScanResponseSchema,
)
from .exceptions import ValidationError
from .logging_config import get_structured_logger

if TYPE_CHECKING:
    from .config import PrivacyAgentConfig

logger = get_structured_logger(__name__)


class InputValidator:
    """Validates Privacy Agent inputs and outputs."""

    def __init__(self, config: "PrivacyAgentConfig") -> None:
        """Initialize the validator.

        Args:
            config: Privacy agent configuration.
        """
        self._config: "PrivacyAgentConfig" = config

    def validate_request(
        self, request: PrivacyScanRequestSchema
    ) -> None:
        """Validate a privacy scan request.

        Args:
            request: The scan request to validate.

        Raises:
            ValidationError: If the request is invalid.
        """
        if not request.text.strip():
            msg: str = "Request text must not be empty"
            raise ValidationError(msg)

        if len(request.text) > 10_000_000:
            msg: str = "Request text exceeds maximum length"
            raise ValidationError(msg)

        if len(request.metadata) > 100:
            msg: str = "Metadata exceeds maximum entry count"
            raise ValidationError(msg)

        logger.debug("Request validation passed")

    def validate_response(
        self, response: PrivacyScanResponseSchema
    ) -> None:
        """Validate a privacy scan response.

        Args:
            response: The scan response to validate.

        Raises:
            ValidationError: If the response is invalid.
        """
        if response.risk_score < 0.0:
            msg: str = "Risk score must be non-negative"
            raise ValidationError(msg)

        if not response.scan_id:
            msg: str = "Scan ID must not be empty"
            raise ValidationError(msg)

        logger.debug("Response validation passed")


class OutputValidator:
    """Validates Privacy Agent outputs."""

    def __init__(self, config: "PrivacyAgentConfig") -> None:
        """Initialize the output validator.

        Args:
            config: Privacy agent configuration.
        """
        self._config: "PrivacyAgentConfig" = config

    def validate_findings(
        self, findings: list[dict]
    ) -> None:
        """Validate structured findings.

        Args:
            findings: List of finding dictionaries.

        Raises:
            ValidationError: If findings are invalid.
        """
        for finding in findings:
            if "severity" not in finding:
                msg: str = (
                    "Each finding must have a severity field"
                )
                raise ValidationError(msg)
            if "category" not in finding:
                msg: str = (
                    "Each finding must have a category field"
                )
                raise ValidationError(msg)

    def validate_recommendations(
        self, recommendations: list[str]
    ) -> None:
        """Validate recommendations list.

        Args:
            recommendations: List of recommendation strings.

        Raises:
            ValidationError: If recommendations are invalid.
        """
        for rec in recommendations:
            if not isinstance(rec, str):
                msg: str = (
                    "Each recommendation must be a string"
                )
                raise ValidationError(msg)
            if not rec.strip():
                msg: str = (
                    "Recommendation text must not be empty"
                )
                raise ValidationError(msg)

