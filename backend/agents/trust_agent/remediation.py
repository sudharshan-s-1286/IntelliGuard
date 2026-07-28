from typing import Any, Dict, List
from pydantic import BaseModel, Field

from agents.trust_agent.decision import ComplianceDecision
from shared.interfaces import DetectorSeverity, FindingDetail
from agents.trust_agent.schemas import (
    DetectorExplanation,
    ExplainabilityReport,
    ScoreExplanation,
    TrustRiskLevel,
)


class ExplanationTemplateConfig(BaseModel):
    """
    Configuration for text templates used to generate explanations.
    Can be overridden for localization or enterprise-specific jargon.
    """

    risk_summaries: Dict[TrustRiskLevel, str] = Field(
        default_factory=lambda: {
            TrustRiskLevel.SAFE: "The payload was evaluated and classified as perfectly safe with no apparent security or compliance risks.",
            TrustRiskLevel.LOW_RISK: "The payload presents a low risk. Minor issues were found but are generally considered acceptable.",
            TrustRiskLevel.MEDIUM_RISK: "The payload presents a medium risk. Potentially sensitive or problematic patterns were detected that require caution.",
            TrustRiskLevel.HIGH_RISK: "The payload presents a high risk. Serious policy violations or threats were detected.",
            TrustRiskLevel.CRITICAL_RISK: "The payload presents a critical risk. Extremely severe threats or violations were detected.",
        }
    )

    decision_recommendations: Dict[ComplianceDecision, List[str]] = Field(
        default_factory=lambda: {
            ComplianceDecision.ALLOW: ["Proceed with standard processing."],
            ComplianceDecision.ALLOW_WITH_WARNING: [
                "Proceed with caution.",
                "Log the payload for periodic audit.",
            ],
            ComplianceDecision.REVIEW: [
                "Halt immediate processing.",
                "Escalate payload to a human moderator or security analyst for review.",
            ],
            ComplianceDecision.BLOCK: [
                "Halt processing immediately.",
                "Reject the request and notify the user of the policy violation.",
            ],
        }
    )

    severity_risk_explanations: Dict[DetectorSeverity, str] = Field(
        default_factory=lambda: {
            DetectorSeverity.CRITICAL: "Poses an immediate and severe threat to system security or data integrity.",
            DetectorSeverity.HIGH: "Presents a significant risk that could lead to policy violations or minor exploits.",
            DetectorSeverity.MEDIUM: "Contains patterns that may be undesirable or mildly sensitive.",
            DetectorSeverity.LOW: "Contains benign or extremely low-impact anomalies.",
            DetectorSeverity.UNKNOWN: "Risk level could not be precisely determined.",
        }
    )

    category_remediations: Dict[str, str] = Field(
        default_factory=lambda: {
            "prompt_injection": "Sanitize user inputs and restrict instruction-override capabilities.",
            "pii": "Redact or mask the sensitive personal information before storage or transmission.",
            "toxicity": "Implement user warnings or mute the offending user account.",
            "hallucination": "Cross-reference the generated claims with authoritative offline sources. Verify all citations, DOIs, and URLs. Adjust model temperature or system prompts to reduce confabulation.",
            "bias": "Review the generated text for discriminatory language or harmful stereotypes. Ensure the prompt or payload uses inclusive language and maintains a neutral, objective tone when discussing protected characteristics.",
        }
    )

    def get_risk_summary(self, risk_level: TrustRiskLevel) -> str:
        return self.risk_summaries.get(
            risk_level, "Risk level classification is unknown."
        )

    def get_decision_recommendations(
        self, decision: ComplianceDecision
    ) -> List[str]:
        return self.decision_recommendations.get(
            decision, ["Review system logs."]
        )

    def get_severity_explanation(self, severity: DetectorSeverity) -> str:
        return self.severity_risk_explanations.get(
            severity, "Impact is unknown."
        )

    def get_remediation(self, category: str) -> str:
        for prefix, remediation in self.category_remediations.items():
            if category.startswith(prefix):
                return remediation
        return "Review the finding and take appropriate domain-specific actions."


class ExplanationBuilder:
    """
    Constructs the human-readable strings from structured data and templates.
    """

    def __init__(self, config: ExplanationTemplateConfig):
        self.config = config

    def build_summary(
        self, risk_level: TrustRiskLevel, decision: ComplianceDecision, finding_count: int
    ) -> str:
        if finding_count == 0:
            return f"Analysis complete: No risks found. Decision is {decision.value}."
        return (
            f"Analysis complete: {finding_count} finding(s) detected resulting in a "
            f"{risk_level.value} classification. The compliance policy decided to {decision.value}."
        )

    def build_detailed_explanation(
        self, score_explanation: ScoreExplanation, findings: List[FindingDetail]
    ) -> str:
        if not findings:
            return "The payload cleanly passed all configured detectors with no deductions."
        
        details = f"The trust score started at {score_explanation.base_score} and was reduced by {score_explanation.total_deduction} points. "
        detector_names = list(score_explanation.detector_contributions.keys())
        details += f"Deductions were applied by the following detectors: {', '.join(detector_names)}."
        return details

    def build_detector_explanations(
        self, findings: List[FindingDetail], score_explanation: ScoreExplanation
    ) -> List[DetectorExplanation]:
        # Group findings by detector for concise reporting
        explanations = []
        detector_groups = {}
        for finding in findings:
            detector_groups.setdefault(finding.detector_name, []).append(finding)

        for det_name, det_findings in detector_groups.items():
            categories = list(set([f.category for f in det_findings]))
            
            # max requires values to be comparable or a key
            # DetectorSeverity is an IntEnum or Enum. Let's use value or a predefined rank map.
            rank = {
                DetectorSeverity.CRITICAL: 4,
                DetectorSeverity.HIGH: 3,
                DetectorSeverity.MEDIUM: 2,
                DetectorSeverity.LOW: 1,
                DetectorSeverity.UNKNOWN: 0
            }
            max_severity = max(det_findings, key=lambda f: rank.get(f.severity, 0)).severity
            
            what_was_detected = f"Detected {len(det_findings)} instance(s) related to: {', '.join(categories)}."
            why_it_is_risky = self.config.get_severity_explanation(max_severity)
            
            deduction = score_explanation.detector_contributions.get(det_name, 0.0)
            score_impact = f"This detector's findings reduced the overall trust score by {deduction} points."

            explanations.append(
                DetectorExplanation(
                    detector_name=det_name,
                    what_was_detected=what_was_detected,
                    why_it_is_risky=why_it_is_risky,
                    score_impact=score_impact,
                )
            )
        return explanations

    def build_remediation_steps(self, findings: List[FindingDetail]) -> List[str]:
        if not findings:
            return ["No remediation required."]
        
        steps = set()
        for finding in findings:
            steps.add(self.config.get_remediation(finding.category))
        return sorted(list(steps))


class ExplainabilityEngine:
    """
    Engine responsible for converting raw data from detectors, scoring, and compliance
    into structured, human-readable ExplainabilityReports.
    """

    def __init__(self, config: ExplanationTemplateConfig = None) -> None:
        self.config = config or ExplanationTemplateConfig()
        self.builder = ExplanationBuilder(self.config)

    def generate_report(
        self,
        findings: List[FindingDetail],
        score_explanation: ScoreExplanation,
        compliance_decision: ComplianceDecision,
        policy_id: str,
    ) -> ExplainabilityReport:
        """
        Generates a full ExplainabilityReport.
        """
        summary = self.builder.build_summary(
            score_explanation.risk_level, compliance_decision, len(findings)
        )
        detailed_explanation = self.builder.build_detailed_explanation(
            score_explanation, findings
        )
        detector_explanations = self.builder.build_detector_explanations(
            findings, score_explanation
        )
        remediation_steps = self.builder.build_remediation_steps(findings)
        risk_summary = self.config.get_risk_summary(score_explanation.risk_level)
        recommended_actions = self.config.get_decision_recommendations(compliance_decision)

        return ExplainabilityReport(
            summary=summary,
            detailed_explanation=detailed_explanation,
            detector_explanations=detector_explanations,
            remediation_steps=remediation_steps,
            risk_summary=risk_summary,
            recommended_actions=recommended_actions,
        )
