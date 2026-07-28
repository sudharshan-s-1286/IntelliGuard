"""Privacy Agent entry point for the IntelliGuard platform."""

from __future__ import annotations

import dataclasses
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from .detector import RegexDetector, create_detector
from .classifier import EntityClassifier
from .masker import PrivacyMasker, RedactionMasker
from .scoring import RiskScorer
from .validator import InputValidator, OutputValidator
from .schemas import (
    OrchestratorRequestSchema,
    OrchestratorResponseSchema,
)
from .config import PrivacyAgentConfig
from .models import PIIEntity, PrivacyFinding
from .logging_config import get_structured_logger
from .exceptions import (
    DetectionError,
    ClassificationError,
    MaskingError,
    ScoringError,
    ValidationError,
)
from .constants import (
    DEFAULT_SCAN_ID_PREFIX,
)

logger = get_structured_logger(__name__)


class PrivacyAgent:
    """Privacy Agent for detecting, classifying, masking, and scoring PII.

    The Privacy Agent is the primary entry point for privacy-related
    analysis within the IntelliGuard platform. It orchestrates the
    detection, classification, masking, and risk scoring of detected
    Personally Identifiable Information (PII) entities.

    This agent does NOT perform security detection, compliance analysis,
    orchestration, API creation, frontend development, or database integration.

    Attributes:
        config: Privacy agent configuration.
        detector: PII detection engine.
        classifier: Entity classification engine.
        masker: Information masking engine.
        scorer: Privacy risk scoring engine.
        input_validator: Input validation engine.
        output_validator: Output validation engine.
    """

    def __init__(
        self,
        config: PrivacyAgentConfig | None = None,
    ) -> None:
        """Initialize the Privacy Agent with its dependencies.

        Args:
            config: Optional configuration override.
                If not provided, default configuration is used.
        """
        self._config: PrivacyAgentConfig = (
            config if config is not None else PrivacyAgentConfig()
        )
        self._detector: RegexDetector = create_detector(
            self._config
        )
        self._classifier: EntityClassifier = EntityClassifier(
            self._config
        )
        self._masker: PrivacyMasker = PrivacyMasker(
            self._config,
            strategy=RedactionMasker(),
        )
        self._scorer: RiskScorer = RiskScorer(
            risk_score_cap=self._config.risk_score_cap,
        )
        self._input_validator: InputValidator = InputValidator(
            self._config
        )
        self._output_validator: OutputValidator = OutputValidator(
            self._config
        )

    def run(self, context: dict) -> dict:
        """Execute the privacy analysis pipeline.

        Args:
            context: A dictionary containing the input data for analysis.
                Expected keys:
                - "request_id" (str): Unique request identifier.
                - "text" (str): The text to scan for PII.
                - "metadata" (dict, optional): Contextual metadata.

        Returns:
            A dictionary containing the privacy analysis results with keys:
            - "status": "success" or "error".
            - "agent": "PrivacyAgent".
            - "request_id": The request identifier from the input.
            - "risk_score": Overall privacy risk score (0-100).
            - "risk_level": "low", "medium", "high", or "critical".
            - "findings": Structured privacy findings.
            - "recommendations": Actionable recommendations.
            - "metadata": Passed through from input.
            - "errors": List of error messages, empty on success.

        Raises:
            This method does not raise exceptions for business logic errors.
            All errors are captured in the "errors" field with status "error".
        """
        logger.info("Starting privacy analysis pipeline")

        errors: list[str] = []
        status = "success"
        entities: list[PIIEntity] = []
        findings: list[PrivacyFinding] = []
        recommendations: list[str] = []
        risk_score_obj = None
        risk_level = ""
        masked_text = ""
        metadata = {}
        request_id = context.get("request_id", "")

        try:
            request = OrchestratorRequestSchema(**context)
            request_id = request.request_id
            text = request.text
            metadata = request.metadata

            self._input_validator.validate_request(request)

            entities = self._detect(text)
            findings = self._build_findings(entities)
            self._output_validator.validate_findings(
                [dataclasses.asdict(f) for f in findings]
            )

            self._classify(entities)
            masked_result = self._mask(text, entities)
            masked_text = masked_result.masked_text
            risk_score_obj = self._score(entities)
            recommendations = self._build_recommendations(
                entities, risk_score_obj
            )
            risk_level = self._calculate_risk_level(
                risk_score_obj.overall_score
            )

        except (PydanticValidationError, ValidationError) as exc:
            status = "error"
            errors.append(str(exc))
            logger.error(
                "Privacy analysis failed: %s", exc, exc_info=True
            )
        except Exception as exc:
            status = "error"
            errors.append(str(exc))
            logger.error(
                "Privacy analysis failed: %s", exc, exc_info=True
            )

        response = OrchestratorResponseSchema(
            status=status,
            agent="PrivacyAgent",
            request_id=request_id,
            risk_score=(
                risk_score_obj.overall_score
                if risk_score_obj is not None
                else 0.0
            ),
            risk_level=risk_level,
            findings=[dataclasses.asdict(f) for f in findings],
            recommendations=recommendations,
            metadata=metadata,
            errors=errors,
        )

        result: dict[str, Any] = response.model_dump()
        logger.info(
            "Privacy analysis complete. status=%s, Entities=%d, Score=%.4f",
            status,
            len(entities),
            risk_score_obj.overall_score if risk_score_obj else 0.0,
        )
        return result

    def _detect(self, text: str) -> list[PIIEntity]:
        """Run PII detection on the input text.

        Args:
            text: Input text to scan.

        Returns:
            List of detected PII entities.

        Raises:
            DetectionError: If detection fails.
        """
        logger.debug("Starting PII detection")
        entities: list[PIIEntity] = self._detector.detect(text)
        logger.info("Detection found %d entities", len(entities))
        return entities

    def _classify(
        self, entities: list[PIIEntity]
    ) -> None:
        """Classify detected PII entities.

        Args:
            entities: List of detected PII entities.

        Raises:
            ClassificationError: If classification fails.
        """
        logger.debug("Classifying %d entities", len(entities))
        self._classifier.classify_batch(entities)

    def _mask(
        self, text: str, entities: list[PIIEntity]
    ) -> Any:
        """Apply masking to detected PII entities.

        Args:
            text: Original text.
            entities: Detected PII entities.

        Returns:
            MaskingResult with the masked text.

        Raises:
            MaskingError: If masking fails.
        """
        logger.debug("Applying masking to %d entities", len(entities))
        return self._masker.mask(text, entities)

    def _score(self, entities: list[PIIEntity]) -> Any:
        """Compute privacy risk score for detected entities.

        Args:
            entities: List of detected PII entities.

        Returns:
            PrivacyRiskScore instance.

        Raises:
            ScoringError: If scoring computation fails.
        """
        logger.debug("Computing risk score for %d entities", len(entities))
        return self._scorer.compute_risk_score(entities)

    def _build_findings(
        self, entities: list[PIIEntity]
    ) -> list[PrivacyFinding]:
        """Build structured privacy findings from detected entities.

        Args:
            entities: List of detected PII entities.

        Returns:
            List of privacy findings.
        """
        findings: list[PrivacyFinding] = []
        if not entities:
            findings.append(
                PrivacyFinding(
                    severity="info",
                    category="privacy",
                    description="No PII entities detected.",
                    entity_count=0,
                    remediation="No action required.",
                )
            )
            return findings

        high_risk: list[PIIEntity] = [
            e for e in entities if e.sensitivity == "high"
        ]
        if high_risk:
            findings.append(
                PrivacyFinding(
                    severity="high",
                    category="high_sensitivity_pii",
                    description=(
                        f"Found {len(high_risk)} high-sensitivity"
                        f" PII entity(s)"
                    ),
                    entity_count=len(high_risk),
                    remediation=(
                        "Implement strict access controls and"
                        " encryption for high-sensitivity PII."
                    ),
                )
            )

        total_count: int = len(entities)
        findings.append(
            PrivacyFinding(
                severity=(
                    "medium" if total_count > 5 else "low"
                ),
                category="entity_count",
                description=(
                    f"Found {total_count} PII entity(s)"
                    f" in the scanned text."
                ),
                entity_count=total_count,
                remediation=(
                    "Review detected PII and apply appropriate"
                    " data protection measures."
                ),
            )
        )

        return findings

    def _build_recommendations(
        self,
        entities: list[PIIEntity],
        risk_score: Any,
    ) -> list[str]:
        """Build recommendations based on findings.

        Args:
            entities: List of detected PII entities.
            risk_score: Computed privacy risk score.

        Returns:
            List of recommendation strings.
        """
        recommendations: list[str] = []

        if risk_score.overall_score > 50.0:
            recommendations.append(
                "High privacy risk detected. Consider implementing"
                " additional data protection measures immediately."
            )

        high_sensitivity_count: int = sum(
            1 for e in entities if e.sensitivity == "high"
        )
        if high_sensitivity_count > 0:
            recommendations.append(
                f"Found {high_sensitivity_count} high-sensitivity"
                " PII entity(ies). Ensure encryption at rest and"
                " in transit."
            )

        if len(entities) > 10:
            recommendations.append(
                "High volume of PII entities detected. Consider"
                " implementing automated data loss prevention"
                " policies."
            )

        if not recommendations:
            recommendations.append(
                "Privacy risk is low. Continue regular data"
                " protection practices."
            )

        return recommendations

    def _calculate_risk_level(self, score: float) -> str:
        """Map a numeric risk score to a risk level string.

        Args:
            score: The overall privacy risk score.

        Returns:
            Risk level string: "low", "medium", "high", or "critical".
        """
        if score >= 75.0:
            return "critical"
        if score >= 50.0:
            return "high"
        if score >= 25.0:
            return "medium"
        return "low"

    def _generate_scan_id(self) -> str:
        """Generate a unique scan identifier.

        Returns:
            Scan ID string.
        """
        import uuid

        return f"{DEFAULT_SCAN_ID_PREFIX}-{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _get_timestamp() -> str:
        """Get the current UTC timestamp in ISO format.

        Returns:
            ISO format timestamp string.
        """
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

