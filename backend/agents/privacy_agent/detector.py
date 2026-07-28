"""PII detection module for the Privacy Agent."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .constants import (
    PII_TYPE_EMAIL,
    PII_TYPE_PHONE,
    PII_TYPE_SSN,
    PII_TYPE_CREDIT_CARD,
    PII_TYPE_IP_ADDRESS,
    PII_TYPE_DATE_OF_BIRTH,
    PII_TYPE_MEDICAL_RECORD,
    PII_SENSITIVITY,
    SENSITIVITY_HIGH,
    SENSITIVITY_MEDIUM,
    SENSITIVITY_LOW,
    DEFAULT_CONFIDENCE_THRESHOLD,
)
from .models import PIIEntity
from .exceptions import DetectionError
from .utils import extract_context, truncate_text, format_entity_for_log
from .logging_config import get_structured_logger

if TYPE_CHECKING:
    from .config import PrivacyAgentConfig

logger = get_structured_logger(__name__)


PII_PATTERNS: dict[str, str] = {
    PII_TYPE_EMAIL: r"""[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}""",
    PII_TYPE_PHONE: r"""(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}""",
    PII_TYPE_SSN: r"""\b\d{3}-\d{2}-\d{4}\b""",
    PII_TYPE_CREDIT_CARD: r"""\b(?:\d{4}[-\s]?){3}\d{4}\b""",
    PII_TYPE_IP_ADDRESS: r"""\b(?:\d{1,3}\.){3}\d{1,3}\b""",
    PII_TYPE_DATE_OF_BIRTH: r"""\b(?:0[1-9]|1[0-2])[-./](?:0[1-9]|[12]\d|3[01])[-./](?:19|20)\d{2}\b""",
    PII_TYPE_MEDICAL_RECORD: r"""\b(?:MR|Medical Record)[\s#:]+[A-Za-z0-9-]+\b""",
}

CREDIT_CARD_BINS: frozenset[str] = frozenset(
    {"4", "5", "37", "6"}
)


@dataclass
class BaseDetector:
    """Abstract base class for PII detectors."""

    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD

    def detect(self, text: str) -> list[PIIEntity]:
        """Detect PII entities in the given text.

        This method must be overridden by subclasses.

        Args:
            text: Input text to scan for PII.

        Returns:
            List of detected PII entities.
        """
        raise NotImplementedError


@dataclass
class RegexDetector(BaseDetector):
    """Regex-based PII detector using predefined patterns."""

    patterns: dict[str, str] = field(default_factory=lambda: dict(PII_PATTERNS))

    def detect(self, text: str) -> list[PIIEntity]:
        """Detect PII entities using regex pattern matching.

        Args:
            text: Input text to scan.

        Returns:
            List of detected PII entities sorted by position.

        Raises:
            DetectionError: If detection fails unexpectedly.
        """
        entities: list[PIIEntity] = []

        try:
            for entity_type, pattern in self.patterns.items():
                compiled: re.Pattern[str] = re.compile(pattern)
                for match in compiled.finditer(text):
                    value: str = match.group()
                    start: int = match.start()
                    end: int = match.end()
                    confidence: float = self._compute_confidence(
                        entity_type, value
                    )

                    if (
                        confidence
                        < self.confidence_threshold
                    ):
                        continue

                    sensitivity: str = PII_SENSITIVITY.get(
                        entity_type, SENSITIVITY_MEDIUM
                    )
                    context: str = extract_context(
                        text, start, end
                    )

                    entity = PIIEntity(
                        entity_type=entity_type,
                        value=value,
                        start=start,
                        end=end,
                        confidence=confidence,
                        sensitivity=sensitivity,
                        context=context,
                    )
                    entities.append(entity)
                    logger.debug(
                        "Detected %s",
                        format_entity_for_log(
                            entity_type, start, end, confidence
                        ),
                    )
        except re.error as exc:
            msg: str = (
                f"Regex compilation error during detection: {exc}"
            )
            raise DetectionError(msg) from exc
        except Exception as exc:
            msg: str = f"Unexpected error during detection: {exc}"
            raise DetectionError(msg) from exc

        entities.sort(key=lambda e: (e.start, e.end))
        return entities

    def _compute_confidence(
        self, entity_type: str, value: str
    ) -> float:
        """Compute a confidence score for a detected entity.

        Args:
            entity_type: The type of PII detected.
            value: The raw detected value.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        base_confidence: float = 0.85

        if entity_type == PII_TYPE_CREDIT_CARD:
            return self._credit_card_confidence(value)
        if entity_type == PII_TYPE_PHONE:
            return self._phone_confidence(value)
        if entity_type == PII_TYPE_EMAIL:
            return self._email_confidence(value)
        if entity_type == PII_TYPE_SSN:
            return self._ssn_confidence(value)

        length_penalty: float = min(
            len(value) / 50.0, 0.1
        )
        return round(max(base_confidence - length_penalty, 0.5), 4)

    @staticmethod
    def _credit_card_confidence(value: str) -> float:
        """Compute confidence for credit card numbers using Luhn check."""
        digits: str = re.sub(r"\D", "", value)
        if not RegexDetector._luhn_check(digits):
            return 0.3
        if len(digits) in {13, 15, 16, 19}:
            return 0.95
        return 0.7

    @staticmethod
    def _phone_confidence(value: str) -> float:
        """Compute confidence for phone numbers."""
        digits: str = re.sub(r"\D", "", value)
        if len(digits) == 10:
            return 0.9
        if len(digits) == 11 and digits.startswith("1"):
            return 0.85
        return 0.5

    @staticmethod
    def _email_confidence(value: str) -> float:
        """Compute confidence for email addresses."""
        if "@" in value and "." in value.split("@")[-1]:
            return 0.92
        return 0.6

    @staticmethod
    def _ssn_confidence(value: str) -> float:
        """Compute confidence for SSN numbers."""
        digits: str = re.sub(r"\D", "", value)
        if len(digits) == 9 and not digits.startswith("000"):
            return 0.9
        return 0.5

    @staticmethod
    def _luhn_check(digits: str) -> bool:
        """Validate a string of digits using the Luhn algorithm."""
        if not digits:
            return False
        reversed_digits: str = digits[::-1]
        total: int = 0
        for i, ch in enumerate(reversed_digits):
            n: int = int(ch)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0


def create_detector(config: "PrivacyAgentConfig") -> RegexDetector:
    """Factory method to create a configured detector instance.

    Args:
        config: Privacy agent configuration.

    Returns:
        Configured RegexDetector instance.
    """
    threshold: float = config.confidence_threshold
    return RegexDetector(confidence_threshold=threshold)


