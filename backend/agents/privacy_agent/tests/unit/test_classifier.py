"""Unit tests for the classifier module."""

from __future__ import annotations

import pytest

from privacy_agent.classifier import EntityClassifier, CLASSIFICATION_RULES
from privacy_agent.models import PIIEntity, EntityCategory
from privacy_agent.exceptions import ClassificationError


def make_entity(
    entity_type: str,
    value: str = "test",
    start: int = 0,
    end: int = 4,
    confidence: float = 0.9,
    sensitivity: str = "medium",
    context: str = "",
) -> PIIEntity:
    """Helper to create a PIIEntity for testing."""
    return PIIEntity(
        entity_type=entity_type,
        value=value,
        start=start,
        end=end,
        confidence=confidence,
        sensitivity=sensitivity,
        context=context,
    )


class TestEntityClassifier:
    """Tests for the EntityClassifier class."""

    def test_classify_email(self) -> None:
        """Test classification of email entity type."""
        classifier = EntityClassifier(None)
        entity = make_entity("email")
        result = classifier.classify(entity)
        assert result.entity_type == "email"
        assert result.category == EntityCategory.CONTACT.value
        assert result.confidence == 0.9

    def test_classify_ssn(self) -> None:
        """Test classification of SSN entity type."""
        classifier = EntityClassifier(None)
        entity = make_entity("ssn")
        result = classifier.classify(entity)
        assert result.category == EntityCategory.GOVERNMENT.value

    def test_classify_credit_card(self) -> None:
        """Test classification of credit card entity type."""
        classifier = EntityClassifier(None)
        entity = make_entity("credit_card")
        result = classifier.classify(entity)
        assert result.category == EntityCategory.FINANCIAL.value

    def test_classify_medical_record(self) -> None:
        """Test classification of medical record entity type."""
        classifier = EntityClassifier(None)
        entity = make_entity("medical_record")
        result = classifier.classify(entity)
        assert result.category == EntityCategory.MEDICAL.value

    def test_classify_unknown_type(self) -> None:
        """Test classification of an unknown entity type falls back."""
        classifier = EntityClassifier(None)
        entity = make_entity("unknown_type")
        result = classifier.classify(entity)
        assert result.category == EntityCategory.IDENTIFYING.value

    def test_classify_batch(self) -> None:
        """Test batch classification of multiple entities."""
        classifier = EntityClassifier(None)
        entities = [
            make_entity("email"),
            make_entity("ssn"),
            make_entity("phone"),
        ]
        results = classifier.classify_batch(entities)
        assert len(results) == 3
        assert results[0].entity_type == "email"
        assert results[1].entity_type == "ssn"
        assert results[2].entity_type == "phone"

    def test_get_risk_category(self) -> None:
        """Test getting risk category for an entity type."""
        classifier = EntityClassifier(None)
        category = classifier.get_risk_category("ssn")
        assert category == EntityCategory.GOVERNMENT.value

    def test_risk_category_coverage(self) -> None:
        """Test that all PII types have classification rules."""
        classifier = EntityClassifier(None)
        known_types = {
            "email", "phone", "ssn", "credit_card",
            "ip_address", "name", "address", "date_of_birth",
            "passport", "driver_license", "medical_record",
            "financial_account",
        }
        for pii_type in known_types:
            category = classifier.get_risk_category(pii_type)
            assert category is not None
            assert isinstance(category, str)
