"""Unit tests for the masker module."""

from __future__ import annotations

import pytest

from privacy_agent.masker import (
    RedactionMasker,
    PartialMasker,
    PrivacyMasker,
    MaskingResult,
)
from privacy_agent.models import PIIEntity
from privacy_agent.config import PrivacyAgentConfig


def make_entity(
    entity_type: str = "email",
    value: str = "user@example.com",
    start: int = 0,
    end: int = 16,
    confidence: float = 0.9,
    sensitivity: str = "high",
    context: str = "",
) -> PIIEntity:
    return PIIEntity(
        entity_type=entity_type,
        value=value,
        start=start,
        end=end,
        confidence=confidence,
        sensitivity=sensitivity,
        context=context,
    )


class TestRedactionMasker:
    """Tests for RedactionMasker."""

    def test_mask_email(self) -> None:
        """Test that email value is fully redacted."""
        masker = RedactionMasker(placeholder="***")
        result = masker.mask("user@example.com")
        assert result == "***"

    def test_mask_empty_string(self) -> None:
        """Test masking of empty string."""
        masker = RedactionMasker()
        result = masker.mask("")
        assert result == ""

    def test_custom_placeholder(self) -> None:
        """Test masking with custom placeholder."""
        masker = RedactionMasker(placeholder="[REDACTED]")
        result = masker.mask("secret")
        assert result == "[REDACTED]"


class TestPartialMasker:
    """Tests for PartialMasker."""

    def test_mask_preserves_prefix_and_suffix(self) -> None:
        """Test that prefix and suffix are preserved."""
        masker = PartialMasker(prefix_chars=2, suffix_chars=3)
        result = masker.mask("user@example.com")
        assert result.startswith("us")
        assert result.endswith("com")

    def test_mask_short_value(self) -> None:
        """Test masking of short values."""
        masker = PartialMasker(prefix_chars=2, suffix_chars=2)
        result = masker.mask("ab")
        assert len(result) == 2
        assert set(result) == {"*"}


class TestPrivacyMasker:
    """Tests for PrivacyMasker."""

    def test_mask_single_entity(self) -> None:
        """Test masking a single entity."""
        config = PrivacyAgentConfig()
        masker = PrivacyMasker(config)
        text = "Email: user@example.com for details."
        entities = [make_entity(start=7, end=23)]
        result = masker.mask(text, entities)
        assert result.masked_count == 1
        assert "***" in result.masked_text

    def test_mask_multiple_entities(self) -> None:
        """Test masking multiple entities."""
        config = PrivacyAgentConfig()
        masker = PrivacyMasker(config)
        text = "SSN 123-45-6789 and email a@b.com."
        entities = [
            make_entity(entity_type="ssn", value="123-45-6789", start=4, end=13),
            make_entity(entity_type="email", value="a@b.com", start=25, end=30),
        ]
        result = masker.mask(text, entities)
        assert result.masked_count == 2

    def test_mask_no_entities(self) -> None:
        """Test masking with no entities returns original text."""
        config = PrivacyAgentConfig()
        masker = PrivacyMasker(config)
        text = "Clean text with no PII."
        result = masker.mask(text, [])
        assert result.masked_text == text
        assert result.masked_count == 0

    def test_mask_entities_in_reverse_order(self) -> None:
        """Test that entities are masked in reverse order to preserve offsets."""
        config = PrivacyAgentConfig()
        masker = PrivacyMasker(config)
        text = "Call 555-123-4567 or email user@test.com."
        entities = [
            make_entity(entity_type="phone", value="555-123-4567", start=4, end=14),
            make_entity(entity_type="email", value="user@test.com", start=23, end=36),
        ]
        result = masker.mask(text, entities)
        assert "***" in result.masked_text
