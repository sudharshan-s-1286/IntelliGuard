import re
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.detectors.base import BaseDetector, DetectorResult, DetectorSeverity, FindingDetail

logger = get_logger(__name__)


class NormalizedPrompt(BaseModel):
    """Normalized representation of an input prompt."""

    original_prompt: str
    normalized_text: str
    char_count: int
    word_count: int


class PromptNormalizer:
    """Utility class for normalizing input prompts prior to rule & heuristic analysis."""

    @classmethod
    def normalize(cls, prompt: str) -> NormalizedPrompt:
        text = prompt or ""
        # Collapse multi-spaces, tabs, newlines into single spaces
        clean_text = re.sub(r"\s+", " ", text).strip()
        normalized = clean_text.lower()
        words = [w for w in normalized.split(" ") if w]
        return NormalizedPrompt(
            original_prompt=text,
            normalized_text=normalized,
            char_count=len(text),
            word_count=len(words),
        )


class PromptInjectionRule(BaseModel):
    """Configurable rule definition model for prompt injection detection."""

    rule_id: str = Field(..., description="Unique rule identifier code (e.g. PI-001)")
    name: str = Field(..., description="Short descriptive rule name")
    description: str = Field(..., description="Detailed description of matched threat")
    severity: DetectorSeverity = Field(
        default=DetectorSeverity.HIGH, description="Severity classification"
    )
    risk_weight: float = Field(
        default=30.0, ge=0.0, le=100.0, description="Risk penalty weight applied when matched"
    )
    pattern: str = Field(..., description="Regex pattern string for matching")
    remediation: str = Field(
        default="Filter or reject input before passing to LLM engine.",
        description="Recommended action to remediate threat",
    )


# Default Rule Set for Offline Prompt Injection Engine
DEFAULT_PROMPT_INJECTION_RULES: List[PromptInjectionRule] = [
    PromptInjectionRule(
        rule_id="PI-001",
        name="ignore_previous_instructions",
        description="Attempts to instruct the model to ignore, disregard, or bypass prior rules or instructions.",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=45.0,
        pattern=r"\b(ignore|disregard|bypass|forget|override)\b.*\b(previous|all|system|above|prior|your)\b.*\b(instructions|directions|prompts|rules|guidelines|context)\b",
        remediation="Reject prompt containing instruction override commands.",
    ),
    PromptInjectionRule(
        rule_id="PI-002",
        name="forget_instructions",
        description="Attempts to clear model memory or erase system instructions.",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        pattern=r"\b(forget|erase|clear|reset)\b.*\b(your|all|previous|system)\b.*\b(instructions|memory|rules|context|prompt)\b",
        remediation="Block attempts to reset system prompt memory.",
    ),
    PromptInjectionRule(
        rule_id="PI-003",
        name="reveal_system_prompt",
        description="Attempts to exfiltrate or reveal the underlying system prompt or internal instructions.",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        pattern=r"\b(reveal|show|display|print|output|repeat|share|write)\b.*\b(the|hidden|internal|initial|secret|system)\b.*\b(prompt|instructions|rules|system_prompt|secrets)\b",
        remediation="Prevent prompt exfiltration attempts.",
    ),
    PromptInjectionRule(
        rule_id="PI-004",
        name="developer_mode",
        description="Attempts to enable unrestricted 'developer mode' or bypass safety modes.",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=45.0,
        pattern=r"\b(developer|dev|unrestricted|god|maintenance)\b\s*\b(mode|state|access|status|override)\b",
        remediation="Sanitize inputs claiming special developer or maintenance status.",
    ),
    PromptInjectionRule(
        rule_id="PI-005",
        name="dan_jailbreak",
        description="Known DAN (Do Anything Now) or jailbreak technique detected.",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=50.0,
        pattern=r"\b(dan|do anything now|jailbreak|jailbroken|jail breaking|persona adoption)\b",
        remediation="Block known jailbreak archetype prompts immediately.",
    ),
    PromptInjectionRule(
        rule_id="PI-006",
        name="admin_override",
        description="Attempts to assume administrative or root authority to bypass restrictions.",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        pattern=r"\b(act as|pretend to be|simulate|assume the role of)\b.*\b(admin|administrator|root|super-user|system administrator|operator)\b",
        remediation="Validate role assumption claims and enforce strict RBAC boundaries.",
    ),
    PromptInjectionRule(
        rule_id="PI-007",
        name="bypass_restrictions",
        description="Explicit request to disable safety filters, policies, or guardrails.",
        severity=DetectorSeverity.HIGH,
        risk_weight=40.0,
        pattern=r"\b(bypass|disable|turn off|override|ignore)\b.*\b(restrictions|safety|policies|guardrails|filters|security|openai policy|content policy)\b",
        remediation="Reject prompts requesting explicit safety filter disabling.",
    ),
    PromptInjectionRule(
        rule_id="PI-008",
        name="reveal_secrets",
        description="Attempts to access hidden keys, secrets, or internal instructions.",
        severity=DetectorSeverity.HIGH,
        risk_weight=30.0,
        pattern=r"\b(reveal|print|show|output)\b.*\b(secrets|confidential|internal instructions|hidden rules|system variables)\b",
        remediation="Enforce strict secret scanning and data loss prevention.",
    ),
    PromptInjectionRule(
        rule_id="PI-009",
        name="simulate_unrestricted_mode",
        description="Attempts to simulate an unrestricted or unfiltered environment.",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        pattern=r"\b(simulate|enter|enable|activate)\b.*\b(unrestricted|unfiltered|sandbox|no rules)\b.*\b(mode|state|environment)?\b",
        remediation="Disallow simulation modes that override safety constraints.",
    ),
    PromptInjectionRule(
        rule_id="PI-010",
        name="direct_injection_term",
        description="Explicit mention of prompt injection or system override attacks.",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        pattern=r"\b(prompt injection|system override|injection attack|override prompt)\b",
        remediation="Inspect prompt for adversarial injection testing.",
    ),
]


class RuleMatch(BaseModel):
    """DTO representing a matched rule instance."""

    rule_id: str
    rule_name: str
    severity: DetectorSeverity
    risk_weight: float
    matched_text: str
    description: str
    remediation: str


class PromptInjectionRuleEngine:
    """Rule engine component evaluating regex rules against normalized prompts."""

    def __init__(self, rules: Optional[List[PromptInjectionRule]] = None) -> None:
        self.rules: List[PromptInjectionRule] = rules if rules is not None else DEFAULT_PROMPT_INJECTION_RULES
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._compile_rules()

    def _compile_rules(self) -> None:
        """Pre-compiles rule regex patterns for high-performance offline evaluation."""
        self._compiled_patterns.clear()
        for rule in self.rules:
            try:
                self._compiled_patterns[rule.rule_id] = re.compile(rule.pattern, re.IGNORECASE)
            except re.error as err:
                logger.error(f"Failed to compile regex for rule {rule.rule_id}: {err}")

    def add_rule(self, rule: PromptInjectionRule) -> None:
        """Dynamically registers a new rule with the engine."""
        self.rules.append(rule)
        self._compiled_patterns[rule.rule_id] = re.compile(rule.pattern, re.IGNORECASE)

    def evaluate(self, normalized: NormalizedPrompt) -> List[RuleMatch]:
        """Evaluates all compiled rules against the normalized prompt text."""
        matches: List[RuleMatch] = []
        for rule in self.rules:
            pattern = self._compiled_patterns.get(rule.rule_id)
            if not pattern:
                continue

            match = pattern.search(normalized.normalized_text)
            if match:
                matches.append(
                    RuleMatch(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        risk_weight=rule.risk_weight,
                        matched_text=match.group(0),
                        description=rule.description,
                        remediation=rule.remediation,
                    )
                )
        return matches


class HeuristicScore(BaseModel):
    """DTO representing heuristic structural analysis outputs."""

    penalty_score: float
    suspicious_verb_count: int
    command_chaining_count: int
    imperative_density: float
    signals: List[str]


class PromptInjectionHeuristics:
    """
    Heuristic analyzer calculating risk metrics based on command density,
    suspicious imperative verbs, and instruction chaining signals.
    """

    SUSPICIOUS_VERBS = {
        "ignore",
        "forget",
        "override",
        "bypass",
        "reveal",
        "disable",
        "disregard",
        "print",
        "simulate",
        "erase",
        "output",
        "show",
    }

    def evaluate(self, normalized: NormalizedPrompt) -> HeuristicScore:
        if normalized.word_count == 0:
            return HeuristicScore(
                penalty_score=0.0,
                suspicious_verb_count=0,
                command_chaining_count=0,
                imperative_density=0.0,
                signals=[],
            )

        words = normalized.normalized_text.split()
        verb_matches = [w for w in words if w in self.SUSPICIOUS_VERBS]
        suspicious_verb_count = len(verb_matches)
        imperative_density = round(suspicious_verb_count / normalized.word_count, 3)

        # Detect command chaining (multiple clauses/commands separated by newlines, semicolons, or delimiters)
        command_delimiters = [";", "&&", "||", "\n", "then ignore"]
        command_chaining_count = sum(
            normalized.original_prompt.count(delim) for delim in command_delimiters
        )

        signals: List[str] = []
        penalty = 0.0

        if suspicious_verb_count >= 3:
            penalty += 20.0
            signals.append(f"High concentration of suspicious imperative verbs ({suspicious_verb_count} found)")
        elif suspicious_verb_count >= 2:
            penalty += 10.0
            signals.append(f"Multiple suspicious imperative verbs detected ({suspicious_verb_count})")

        if command_chaining_count >= 2:
            penalty += 15.0
            signals.append(f"Instruction chaining pattern detected ({command_chaining_count} command delimiters)")

        if imperative_density > 0.3 and normalized.word_count > 4:
            penalty += 15.0
            signals.append(f"Excessive imperative language density ({imperative_density * 100:.1f}%)")

        return HeuristicScore(
            penalty_score=min(penalty, 50.0),
            suspicious_verb_count=suspicious_verb_count,
            command_chaining_count=command_chaining_count,
            imperative_density=imperative_density,
            signals=signals,
        )


class PromptInjectionDetector(BaseDetector):
    """
    Production-ready offline Prompt Injection Detector.
    
    Combines a configurable regex rule engine with heuristic risk analysis to detect
    instruction overrides, jailbreaks, system prompt exfiltration, and developer mode bypasses.
    """

    def __init__(
        self,
        rule_engine: Optional[PromptInjectionRuleEngine] = None,
        heuristics: Optional[PromptInjectionHeuristics] = None,
    ) -> None:
        self.rule_engine = rule_engine or PromptInjectionRuleEngine()
        self.heuristics = heuristics or PromptInjectionHeuristics()

    @property
    def name(self) -> str:
        return "prompt_injection_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        start_time = time.perf_counter()

        # Handle empty/whitespace input gracefully
        if not prompt or not prompt.strip():
            execution_time = round((time.perf_counter() - start_time) * 1000, 2)
            return DetectorResult(
                detector_name=self.name,
                is_triggered=False,
                score=100.0,
                findings=[],
                execution_time_ms=execution_time,
                metadata={"status": "empty_prompt"},
            )

        # Step 1: Input Normalization
        normalized = PromptNormalizer.normalize(prompt)

        # Step 2: Rule Engine Evaluation
        rule_matches = self.rule_engine.evaluate(normalized)

        # Step 3: Heuristic Risk Evaluation
        heuristic_res = self.heuristics.evaluate(normalized)

        # Step 4: Risk Assessment Calculation
        rule_penalty = sum(match.risk_weight for match in rule_matches)
        total_penalty = rule_penalty + heuristic_res.penalty_score
        calculated_score = round(max(0.0, min(100.0, 100.0 - total_penalty)), 2)

        is_triggered = (
            len(rule_matches) > 0
            or heuristic_res.penalty_score >= 15.0
            or calculated_score < 75.0
        )

        # Step 5: Finding Generation
        findings: List[FindingDetail] = []
        for match in rule_matches:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category=f"prompt_injection.{match.rule_name}",
                    severity=match.severity,
                    description=f"Rule [{match.rule_id}] Triggered: {match.description}",
                    confidence_score=0.95,
                    metadata={
                        "rule_id": match.rule_id,
                        "matched_text": match.matched_text,
                        "risk_weight": match.risk_weight,
                        "remediation": match.remediation,
                    },
                )
            )

        if heuristic_res.signals and not rule_matches:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="prompt_injection.heuristic_anomaly",
                    severity=DetectorSeverity.MEDIUM,
                    description=f"Heuristic structural risk detected: {'; '.join(heuristic_res.signals)}",
                    confidence_score=0.75,
                    metadata={
                        "heuristic_penalty": heuristic_res.penalty_score,
                        "signals": heuristic_res.signals,
                    },
                )
            )

        execution_time = round((time.perf_counter() - start_time) * 1000, 2)

        return DetectorResult(
            detector_name=self.name,
            is_triggered=is_triggered,
            score=calculated_score,
            findings=findings,
            execution_time_ms=execution_time,
            metadata={
                "rules_matched_count": len(rule_matches),
                "matched_rule_ids": [m.rule_id for m in rule_matches],
                "heuristic_penalty": heuristic_res.penalty_score,
                "word_count": normalized.word_count,
            },
        )
