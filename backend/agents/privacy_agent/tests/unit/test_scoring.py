"""Unit tests for the scoring module."""

from __future__ import annotations

import pytest

from privacy_agent.scoring import RiskScorer
from privacy_agent.models import PIIEntity
from privacy_agent.constants import DEFAULT_RISK_SCORE_CAP


def make_entity(
    entity_type: str = "email",
    value: str = "user@example.com",
    start: int = 0,
    end: int = 16,
    confidence: float = 0.9,
    sensitivity: str = "medium",
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


class TestRiskScorer:
    """Tests for the RiskScorer class."""

    def test_compute_score_with_no_entities(self) -> None:
        """Test scoring with no entities returns zero."""
        scorer = RiskScorer()
        result = scorer.compute_risk_score([])
        assert result.overall_score == 0.0

    def test_compute_score_with_entities(self) -> None:
        """Test scoring with detected entities."""
        scorer = RiskScorer()
        entities = [
            make_entity(entity_type="email", confidence=0.9),
            make_entity(entity_type="phone", confidence=0.8),
        ]
        result = scorer.compute_risk_score(entities)
        assert result.overall_score > 0.0

    def test_score_is_capped(self) -> None:
        """Test that the score does not exceed the cap."""
        scorer = RiskScorer(risk_score_cap=50.0)
        entities = [
            make_entity(entity_type="ssn", confidence=1.0, sensitivity="high"),
            make_entity(entity_type="credit_card", confidence=1.0, sensitivity="high"),
            make_entity(entity_type="passport", confidence=1.0, sensitivity="high"),
        ]
        result = scorer.compute_risk_score(entities)
        assert result.overall_score <= 50.0

    def test_high_sensitivity_weighted_higher(self) -> None:
        """Test that high sensitivity entities contribute more to the score."""
        scorer = RiskScorer()
        high_sensitivity = [
            make_entity(entity_type="ssn", confidence=0.9, sensitivity="high"),
        ]
        low_sensitivity = [
            make_entity(entity_type="name", confidence=0.9, sensitivity="low"),
        ]
        high_result = scorer.compute_risk_score(high_sensitivity)
        low_result = scorer.compute_risk_score(low_sensitivity)
        assert high_result.overall_score > low_result.overall_score

    def test_sensitivity_breakdown(self) -> None:
        """Test that sensitivity breakdown is populated."""
        scorer = RiskScorer()
        entities = [
            make_entity(entity_type="ssn", confidence=0.9, sensitivity="high"),
            make_entity(entity_type="email", confidence=0.8, sensitivity="medium"),
        ]
        result = scorer.compute_risk_score(entities)
        assert "high" in result.sensitivity_breakdown
        assert "medium" in result.sensitivity_breakdown

    def test_entity_scores_populated(self) -> None:
        """Test that individual entity scores are recorded."""
        scorer = RiskScorer()
        entities = [
            make_entity(entity_type="email", confidence=0.9),
        ]
        result = scorer.compute_risk_score(entities)
        assert len(result.entity_scores) == 1
        assert result.entity_scores[0]["entity_type"] == "email"

    def test_category_scores_populated(self) -> None:
        """Test that category scores are recorded."""
        scorer = RiskScorer()
        entities = [
            make_entity(entity_type="email", confidence=0.9),
            make_entity(entity_type="phone", confidence=0.9),
        ]
        result = scorer.compute_risk_score(entities)
        assert len(result.category_scores) > 0
