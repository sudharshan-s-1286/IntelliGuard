"""Unit tests for the PII detector module."""

from __future__ import annotations

import pytest

from privacy_agent.detector import RegexDetector, PII_PATTERNS
from privacy_agent.constants import (
    PII_TYPE_EMAIL,
    PII_TYPE_SSN,
    PII_TYPE_CREDIT_CARD,
    PII_TYPE_PHONE,
    DEFAULT_CONFIDENCE_THRESHOLD,
)
from privacy_agent.models import PIIEntity


class TestRegexDetector:
    """Tests for the RegexDetector class."""

    def test_init_with_default_threshold(self) -> None:
        """Test initialization with default confidence threshold."""
        detector = RegexDetector()
        assert detector.confidence_threshold == DEFAULT_CONFIDENCE_THRESHOLD

    def test_init_with_custom_threshold(self) -> None:
        """Test initialization with custom confidence threshold."""
        detector = RegexDetector(confidence_threshold=0.8)
        assert detector.confidence_threshold == 0.8

    def test_detect_email(self) -> None:
        """Test detection of email addresses."""
        detector = RegexDetector()
        text = "Contact us at user@example.com for assistance."
        entities = detector.detect(text)
        assert len(entities) > 0
        assert entities[0].entity_type == PII_TYPE_EMAIL
        assert entities[0].value == "user@example.com"

    def test_detect_ssn(self) -> None:
        """Test detection of SSN numbers."""
        detector = RegexDetector()
        text = "My SSN is 123-45-6789."
        entities = detector.detect(text)
        assert len(entities) > 0
        assert entities[0].entity_type == PII_TYPE_SSN
        assert entities[0].value == "123-45-6789"

    def test_detect_credit_card(self) -> None:
        """Test detection of credit card numbers."""
        detector = RegexDetector()
        text = "My card is 4111-1111-1111-1111."
        entities = detector.detect(text)
        assert len(entities) > 0
        assert entities[0].entity_type == PII_TYPE_CREDIT_CARD

    def test_detect_phone(self) -> None:
        """Test detection of phone numbers."""
        detector = RegexDetector()
        text = "Call me at (555) 123-4567."
        entities = detector.detect(text)
        assert len(entities) > 0
        assert entities[0].entity_type == PII_TYPE_PHONE

    def test_detect_no_entities(self) -> None:
        """Test detection when no PII is present."""
        detector = RegexDetector()
        text = "This is a completely clean text with no PII."
        entities = detector.detect(text)
        assert len(entities) == 0

    def test_detect_multiple_entities(self) -> None:
        """Test detection of multiple entities in one text."""
        detector = RegexDetector()
        text = (
            "Email alice@example.com and call 555-123-4567."
            " SSN: 987-65-4321."
        )
        entities = detector.detect(text)
        assert len(entities) == 3

    def test_detect_returns_sorted_by_position(self) -> None:
        """Test that entities are returned sorted by position."""
        detector = RegexDetector()
        text = "SSN 123-45-6789 and email test@test.com."
        entities = detector.detect(text)
        assert entities[0].start <= entities[1].start

    def test_detect_empty_text(self) -> None:
        """Test detection on empty text."""
        detector = RegexDetector()
        entities = detector.detect("")
        assert len(entities) == 0

    def test_detect_returns_correct_offsets(self) -> None:
        """Test that entity start and end offsets are correct."""
        detector = RegexDetector()
        text = "Contact: user@domain.com"
        entities = detector.detect(text)
        assert len(entities) > 0
        entity = entities[0]
        assert text[entity.start:entity.end] == entity.value

    def test_detect_entity_has_context(self) -> None:
        """Test that detected entities include context."""
        detector = RegexDetector()
        text = "Email admin@company.com for the report."
        entities = detector.detect(text)
        assert len(entities) > 0
        assert len(entities[0].context) > 0
