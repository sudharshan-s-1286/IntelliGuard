from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from shared.logger import get_logger
from shared.interfaces import DetectorResult, DetectorSeverity, FindingDetail

logger = get_logger(__name__)


class ComplianceDecision(str, Enum):
    """
    Standardized Compliance Decisions enforced by the Compliance Policy Engine.
    """

    ALLOW = "ALLOW"
    ALLOW_WITH_WARNING = "ALLOW_WITH_WARNING"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class PolicyRule(BaseModel):
    """
    Configurable compliance policy rule definition model.
    """

    rule_id: str = Field(..., description="Unique policy rule identifier (e.g. POLICY-BLOCK-CRITICAL)")
    name: str = Field(..., description="Short descriptive rule name")
    decision: ComplianceDecision = Field(..., description="Decision to enforce if rule matches")
    priority: int = Field(
        default=50, description="Rule evaluation priority (lower value = higher precedence)"
    )
    exact_severity: Optional[DetectorSeverity] = Field(
        default=None, description="Exact finding severity required to trigger rule"
    )
    min_severity: Optional[DetectorSeverity] = Field(
        default=None, description="Minimum finding severity required to trigger rule"
    )
    required_category_prefix: Optional[str] = Field(
        default=None, description="Matching category prefix filter (e.g. prompt_injection, pii.openai_api_key)"
    )
    max_trust_score: Optional[float] = Field(
        default=None, description="Threshold triggering rule if overall trust score <= max_trust_score"
    )
    description: str = Field(..., description="Detailed description of rule policy logic")


# Default Enterprise Security & Privacy Policy Rules
DEFAULT_POLICY_RULES: List[PolicyRule] = [
    # Priority 10: Block any CRITICAL severity finding immediately
    PolicyRule(
        rule_id="POLICY-CRITICAL-SEVERITY-BLOCK",
        name="Block Critical Severity Threats",
        decision=ComplianceDecision.BLOCK,
        priority=10,
        exact_severity=DetectorSeverity.CRITICAL,
        description="Blocks request payload if any CRITICAL severity threat finding is detected.",
    ),
    # Priority 20: Block if overall trust score <= 40.0
    PolicyRule(
        rule_id="POLICY-TRUST-SCORE-CRITICAL-BLOCK",
        name="Block Low Trust Score",
        decision=ComplianceDecision.BLOCK,
        priority=20,
        max_trust_score=40.0,
        description="Blocks request payload if aggregated trust score drops to 40.0 or below.",
    ),
    # Priority 30: Review for HIGH severity findings
    PolicyRule(
        rule_id="POLICY-HIGH-SEVERITY-REVIEW",
        name="Review High Severity Risks",
        decision=ComplianceDecision.REVIEW,
        priority=30,
        exact_severity=DetectorSeverity.HIGH,
        description="Flags payload for human/secondary review if HIGH severity findings are detected.",
    ),
    # Priority 35: Review for degraded trust score <= 70.0
    PolicyRule(
        rule_id="POLICY-TRUST-SCORE-REVIEW",
        name="Review Degraded Trust Score",
        decision=ComplianceDecision.REVIEW,
        priority=35,
        max_trust_score=70.0,
        description="Flags payload for review if aggregated trust score is between 40.1 and 70.0.",
    ),
    # Priority 40: Allow with Warning for MEDIUM severity findings
    PolicyRule(
        rule_id="POLICY-MEDIUM-SEVERITY-WARNING",
        name="Allow With Warning For Medium Findings",
        decision=ComplianceDecision.ALLOW_WITH_WARNING,
        priority=40,
        exact_severity=DetectorSeverity.MEDIUM,
        description="Allows payload with warning flags when MEDIUM severity findings are present.",
    ),
    # Priority 50: Default Fallback ALLOW
    PolicyRule(
        rule_id="POLICY-DEFAULT-ALLOW",
        name="Default Policy Allow",
        decision=ComplianceDecision.ALLOW,
        priority=50,
        description="Default fallback policy allowing clean payloads with zero risk triggers.",
    ),
]


class CompliancePolicy(BaseModel):
    """
    Multi-tenant Compliance Policy container model.
    """

    policy_id: str = Field(default="default-enterprise-policy", description="Unique policy configuration ID")
    name: str = Field(default="Standard Enterprise Security Policy", description="Human-readable policy name")
    rules: List[PolicyRule] = Field(
        default_factory=lambda: DEFAULT_POLICY_RULES, description="List of policy rules"
    )


class ComplianceEngine:
    """
    Centralized Compliance Policy Engine.
    
    Evaluates aggregated detector findings and unified trust scores against configurable
    policy rules to determine official security decisions (ALLOW, ALLOW_WITH_WARNING, REVIEW, BLOCK).
    """

    SEVERITY_ORDER = {
        DetectorSeverity.UNKNOWN: 0,
        DetectorSeverity.LOW: 1,
        DetectorSeverity.MEDIUM: 2,
        DetectorSeverity.HIGH: 3,
        DetectorSeverity.CRITICAL: 4,
    }

    def __init__(self, policy: Optional[CompliancePolicy] = None) -> None:
        self.policy: CompliancePolicy = policy or CompliancePolicy()
        self._sort_rules()
        logger.info(f"ComplianceEngine initialized with policy [{self.policy.policy_id}]")

    def _sort_rules(self) -> None:
        """Sorts policy rules by ascending priority (lower priority int = higher precedence)."""
        self.policy.rules.sort(key=lambda r: r.priority)

    def evaluate(
        self, trust_score: float, findings: List[FindingDetail]
    ) -> Dict[str, Any]:
        """
        Evaluates trust score and aggregated findings against sorted policy rules.
        Returns a dict payload containing 'decision', 'policy_id', and 'matched_rule_id'.
        """
        for rule in self.policy.rules:
            if self._matches_rule(rule, trust_score, findings):
                logger.info(
                    f"Compliance decision [{rule.decision.value}] triggered by rule [{rule.rule_id}]"
                )
                return {
                    "decision": rule.decision,
                    "policy_id": self.policy.policy_id,
                    "matched_rule_id": rule.rule_id,
                }

        # Fallback default decision if no rules match
        return {
            "decision": ComplianceDecision.ALLOW,
            "policy_id": self.policy.policy_id,
            "matched_rule_id": "DEFAULT-FALLBACK",
        }

    def _matches_rule(
        self, rule: PolicyRule, trust_score: float, findings: List[FindingDetail]
    ) -> bool:
        """Helper checking if a single PolicyRule matches the current score and findings context."""
        # 1. Unconditional rule (no filter criteria set) matches anything as fallback
        if (
            rule.exact_severity is None
            and rule.min_severity is None
            and rule.required_category_prefix is None
            and rule.max_trust_score is None
        ):
            return True

        # 2. Max trust score trigger
        if rule.max_trust_score is not None and trust_score <= rule.max_trust_score:
            return True

        # 3. Finding criteria triggers
        if not findings:
            return False

        for finding in findings:
            exact_matches = True
            if rule.exact_severity is not None:
                exact_matches = finding.severity == rule.exact_severity

            severity_matches = True
            if rule.min_severity is not None:
                finding_sev_rank = self.SEVERITY_ORDER.get(finding.severity, 0)
                target_sev_rank = self.SEVERITY_ORDER.get(rule.min_severity, 0)
                severity_matches = finding_sev_rank >= target_sev_rank

            category_matches = True
            if rule.required_category_prefix is not None:
                category_matches = finding.category.startswith(rule.required_category_prefix)

            if (
                exact_matches
                and severity_matches
                and category_matches
                and (
                    rule.exact_severity is not None
                    or rule.min_severity is not None
                    or rule.required_category_prefix is not None
                )
            ):
                return True

        return False


