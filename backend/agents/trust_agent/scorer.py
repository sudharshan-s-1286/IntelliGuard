from typing import Dict, List
from pydantic import BaseModel, Field

from shared.logger import get_logger
from shared.interfaces import DetectorSeverity, FindingDetail
from agents.trust_agent.schemas import ScoreExplanation, TrustRiskLevel

logger = get_logger(__name__)


class DetectorWeightConfig(BaseModel):
    """
    Configuration mapping detector names to their respective penalty weights.
    """
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "prompt_injection_detector": 1.0,
            "pii_detector": 0.8,
            "toxicity_detector": 0.6,
        },
        description="Dictionary mapping detector internal names to scoring weights (0.0 to 1.0+)",
    )
    default_weight: float = Field(
        default=0.5, description="Fallback weight for unknown detectors"
    )

    def get_weight(self, detector_name: str) -> float:
        return self.weights.get(detector_name, self.default_weight)


class TrustScoreEngine:
    """
    Independent engine calculating the unified trust score based on detector findings.
    Applies configurable weights, diminishing returns for duplicate findings, and severity mapping.
    """

    SEVERITY_MULTIPLIER = {
        DetectorSeverity.UNKNOWN: 0.0,
        DetectorSeverity.LOW: 0.1,
        DetectorSeverity.MEDIUM: 0.3,
        DetectorSeverity.HIGH: 0.6,
        DetectorSeverity.CRITICAL: 1.0,
    }

    def __init__(self, config: DetectorWeightConfig = None) -> None:
        self.config = config or DetectorWeightConfig()
        logger.info("TrustScoreEngine initialized")

    def _map_risk_level(self, score: float) -> TrustRiskLevel:
        if score >= 90.0:
            return TrustRiskLevel.SAFE
        elif score >= 75.0:
            return TrustRiskLevel.LOW_RISK
        elif score >= 50.0:
            return TrustRiskLevel.MEDIUM_RISK
        elif score >= 25.0:
            return TrustRiskLevel.HIGH_RISK
        else:
            return TrustRiskLevel.CRITICAL_RISK

    def calculate(self, findings: List[FindingDetail]) -> ScoreExplanation:
        """
        Calculates the overall trust score explanation metadata and risk level based on the findings.
        """
        base_score = 100.0
        
        # We group identical findings by detector and category to apply diminishing returns
        finding_counts: Dict[str, int] = {}
        detector_contributions: Dict[str, float] = {}
        severity_contributions: Dict[str, float] = {}

        total_deduction = 0.0

        # Sort findings by severity (descending) and confidence (descending) 
        # so highest impact duplicates are evaluated first before decay applies.
        severity_rank = {
            DetectorSeverity.CRITICAL: 4,
            DetectorSeverity.HIGH: 3,
            DetectorSeverity.MEDIUM: 2,
            DetectorSeverity.LOW: 1,
            DetectorSeverity.UNKNOWN: 0
        }
        
        sorted_findings = sorted(
            findings, 
            key=lambda f: (severity_rank.get(f.severity, 0), f.confidence_score), 
            reverse=True
        )

        for finding in sorted_findings:
            detector_name = finding.detector_name
            category = finding.category
            severity = finding.severity
            
            # Uniqueness key for diminishing returns
            group_key = f"{detector_name}::{category}"
            count = finding_counts.get(group_key, 0)
            finding_counts[group_key] = count + 1

            # Base parameters
            sev_multiplier = self.SEVERITY_MULTIPLIER.get(severity, 0.0)
            det_weight = self.config.get_weight(detector_name)
            confidence = finding.confidence_score

            # Diminishing returns factor: 1.0 for first finding, 0.5 for second, 0.25 for third...
            decay_factor = 0.5 ** count

            # Deduction formula
            deduction = 100.0 * sev_multiplier * det_weight * confidence * decay_factor
            
            # Aggregate
            total_deduction += deduction
            detector_contributions[detector_name] = detector_contributions.get(detector_name, 0.0) + deduction
            severity_name = severity.value
            severity_contributions[severity_name] = severity_contributions.get(severity_name, 0.0) + deduction

        # Normalize score bounds
        final_score = base_score - total_deduction
        if final_score < 0.0:
            final_score = 0.0
        elif final_score > 100.0:
            final_score = 100.0

        final_score = round(final_score, 2)
        total_deduction = round(base_score - final_score, 2)
        
        # Round contributions
        for k in detector_contributions:
            detector_contributions[k] = round(detector_contributions[k], 2)
        for k in severity_contributions:
            severity_contributions[k] = round(severity_contributions[k], 2)

        risk_level = self._map_risk_level(final_score)

        return ScoreExplanation(
            base_score=base_score,
            total_deduction=total_deduction,
            detector_contributions=detector_contributions,
            severity_contributions=severity_contributions,
            risk_level=risk_level
        )
