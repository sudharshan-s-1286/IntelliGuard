"""Custom exceptions for the Privacy Agent."""

from __future__ import annotations


class PrivacyAgentError(Exception):
    """Base exception for all Privacy Agent errors."""


class DetectionError(PrivacyAgentError):
    """Raised when PII detection fails."""


class ClassificationError(PrivacyAgentError):
    """Raised when entity classification fails."""


class MaskingError(PrivacyAgentError):
    """Raised when information masking fails."""


class ScoringError(PrivacyAgentError):
    """Raised when risk scoring fails."""


class ValidationError(PrivacyAgentError):
    """Raised when input validation fails."""


class ConfigurationError(PrivacyAgentError):
    """Raised when configuration is invalid."""
