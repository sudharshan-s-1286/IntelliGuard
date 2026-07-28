"""PII entity classification module for the Privacy Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .constants import (
    PII_TYPE_EMAIL,
    PII_TYPE_PHONE,
    PII_TYPE_SSN,
    PII_TYPE_CREDIT_CARD,
    PII_TYPE_IP_ADDRESS,
    PII_TYPE_NAME,
    PII_TYPE_ADDRESS,
    PII_TYPE_DATE_OF_BIRTH,
    PII_TYPE_PASSPORT,
    PII_TYPE_DRIVER_LICENSE,
    PII_TYPE_MEDICAL_RECORD,
    PII_TYPE_FINANCIAL_ACCOUNT,
)
from .models import PIIEntity, EntityCategory
from .exceptions import ClassificationError
from .logging_config import get_structured_logger

if TYPE_CHECKING:
    from .config import PrivacyAgentConfig

logger = get_structured_logger(__name__)


CLASSIFICATION_RULES: dict[str, EntityCategory] = {
    PII_TYPE_EMAIL: EntityCategory.CONTACT,
    PII_TYPE_PHONE: EntityCategory.CONTACT,
    PII_TYPE_IP_ADDRESS: EntityCategory.CONTACT,
    PII_TYPE_SSN: EntityCategory.GOVERNMENT,
    PII_TYPE_PASSPORT: EntityCategory.GOVERNMENT,
    PII_TYPE_DRIVER_LICENSE: EntityCategory.GOVERNMENT,
    PII_TYPE_CREDIT_CARD: EntityCategory.FINANCIAL,
    PII_TYPE_FINANCIAL_ACCOUNT: EntityCategory.FINANCIAL,
    PII_TYPE_MEDICAL_RECORD: EntityCategory.MEDICAL,
    PII_TYPE_NAME: EntityCategory.DEMOGRAPHIC,
    PII_TYPE_ADDRESS: EntityCategory.DEMOGRAPHIC,
    PII_TYPE_DATE_OF_BIRTH: EntityCategory.DEMOGRAPHIC,
}


@dataclass
class ClassificationResult:
    """Result of entity classification."""

    entity_type: str
    category: str
    confidence: float


class EntityClassifier:
    """Classifies detected PII entities into categories."""

    def __init__(self, config: "PrivacyAgentConfig") -> None:
        """Initialize the classifier with configuration.

        Args:
            config: Privacy agent configuration.
        """
        self._config: "PrivacyAgentConfig" = config
        self._rules: dict[str, EntityCategory] = CLASSIFICATION_RULES

    def classify(
        self, entity: PIIEntity
    ) -> ClassificationResult:
        """Classify a single PII entity.

        Args:
            entity: The PII entity to classify.

        Returns:
            Classification result with category and confidence.

        Raises:
            ClassificationError: If classification fails.
        """
        try:
            category: EntityCategory = self._rules.get(
                entity.entity_type, EntityCategory.IDENTIFYING
            )
            confidence: float = entity.confidence

            result: ClassificationResult = ClassificationResult(
                entity_type=entity.entity_type,
                category=category.value,
                confidence=confidence,
            )

            logger.debug(
                "Classified entity_type=%s as category=%s",
                entity.entity_type,
                category.value,
            )
            return result
        except Exception as exc:
            msg: str = (
                f"Classification failed for entity"
                f" {entity.entity_type}: {exc}"
            )
            raise ClassificationError(msg) from exc

    def classify_batch(
        self, entities: list[PIIEntity]
    ) -> list[ClassificationResult]:
        """Classify a batch of PII entities.

        Args:
            entities: List of PII entities to classify.

        Returns:
            List of classification results.
        """
        return [self.classify(e) for e in entities]

    def get_risk_category(self, entity_type: str) -> str:
        """Get the risk category for an entity type.

        Args:
            entity_type: The PII entity type.

        Returns:
            Risk category string.
        """
        category: EntityCategory = self._rules.get(
            entity_type, EntityCategory.IDENTIFYING
        )
        return category.value

