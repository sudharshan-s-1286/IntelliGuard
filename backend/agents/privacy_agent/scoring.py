"""Privacy risk scoring module for the Privacy Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models import PIIEntity, PrivacyRiskScore
from .constants import SENSITIVITY_WEIGHTS
from .exceptions import ScoringError
from .logging_config import get_structured_logger

if TYPE_CHECKING:
    from .config import PrivacyAgentConfig

logger = get_structured_logger(__name__)


@dataclass
class RiskScorer:
    """Computes privacy risk scores from detected PII entities."""

    risk_score_cap: float = 100.0

    def compute_risk_score(
        self,
        entities: list[PIIEntity],
    ) -> PrivacyRiskScore:
        """Compute the overall privacy risk score.

        The score is calculated as a weighted sum of each entity
        contribution, where the weight is determined by the
        entity sensitivity level and confidence score.

        Args:
            entities: List of detected PII entities.

        Returns:
            PrivacyRiskScore with the overall score and breakdown.

        Raises:
            ScoringError: If scoring computation fails.
        """
        if not entities:
            return PrivacyRiskScore()

        try:
            sensitivity_scores: dict[str, float] = {}
            category_scores: dict[str, float] = {}
            entity_score_list: list[dict] = []
            total_weighted: float = 0.0

            for entity in entities:
                weight: float = SENSITIVITY_WEIGHTS.get(
                    entity.sensitivity, 0.5
                )
                entity_score: float = (
                    entity.confidence * weight * 10.0
                )
                total_weighted += entity_score

                sensitivity_scores[
                    entity.sensitivity
                ] = sensitivity_scores.get(
                    entity.sensitivity, 0.0
                ) + entity_score

                category: str = self._categorize(
                    entity.entity_type
                )
                category_scores[
                    category
                ] = category_scores.get(
                    category, 0.0
                ) + entity_score

                entity_score_list.append(
                    {
                        "entity_type": entity.entity_type,
                        "confidence": entity.confidence,
                        "sensitivity": entity.sensitivity,
                        "score": round(entity_score, 4),
                    }
                )

            raw_score: float = min(total_weighted, self.risk_score_cap)

            result: PrivacyRiskScore = PrivacyRiskScore(
                overall_score=round(raw_score, 4),
                entity_scores=entity_score_list,
                sensitivity_breakdown={
                    k: round(v, 4)
                    for k, v in sensitivity_scores.items()
                },
                category_scores={
                    k: round(v, 4)
                    for k, v in category_scores.items()
                },
            )

            logger.info(
                "Computed risk score: %.4f for %d entities",
                result.overall_score,
                len(entities),
            )
            return result
        except Exception as exc:
            msg: str = (
                f"Failed to compute privacy risk score: {exc}"
            )
            raise ScoringError(msg) from exc

    @staticmethod
    def _categorize(entity_type: str) -> str:
        """Map an entity type to a high-level category.

        Args:
            entity_type: The PII entity type string.

        Returns:
            The entity category string.
        """
        financial_types: frozenset[str] = frozenset(
            {
                "credit_card",
                "financial_account",
            }
        )
        government_types: frozenset[str] = frozenset(
            {
                "ssn",
                "passport",
                "driver_license",
            }
        )
        medical_types: frozenset[str] = frozenset(
            {
                "medical_record",
            }
        )
        contact_types: frozenset[str] = frozenset(
            {
                "email",
                "phone",
                "ip_address",
            }
        )

        if entity_type in financial_types:
            return "financial"
        if entity_type in government_types:
            return "government"
        if entity_type in medical_types:
            return "medical"
        if entity_type in contact_types:
            return "contact"
        if entity_type in {
            "name",
            "address",
            "date_of_birth",
        }:
            return "demographic"
        return "identifying"

