import re
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from shared.logger import get_logger
from shared.interfaces import BaseDetector, DetectorResult, DetectorSeverity, FindingDetail

logger = get_logger(__name__)


class PIIEntityType(str, Enum):
    """Supported PII and Sensitive Entity Types."""

    EMAIL = "EMAIL"
    PHONE_NUMBER = "PHONE_NUMBER"
    CREDIT_CARD = "CREDIT_CARD"
    IPV4_ADDRESS = "IPV4_ADDRESS"
    IPV6_ADDRESS = "IPV6_ADDRESS"
    API_KEY_GENERIC = "API_KEY_GENERIC"
    JWT_TOKEN = "JWT_TOKEN"
    US_SSN = "US_SSN"
    IN_AADHAAR = "IN_AADHAAR"
    IN_PAN = "IN_PAN"
    PASSPORT_NUMBER = "PASSPORT_NUMBER"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    URL_ACCESS_TOKEN = "URL_ACCESS_TOKEN"
    AWS_ACCESS_KEY = "AWS_ACCESS_KEY"
    GITHUB_TOKEN = "GITHUB_TOKEN"
    GOOGLE_API_KEY = "GOOGLE_API_KEY"
    BEARER_TOKEN = "BEARER_TOKEN"
    OPENAI_API_KEY = "OPENAI_API_KEY"
    GENERIC_SECRET = "GENERIC_SECRET"


class PIIMasker:
    """Utility class providing entity-specific masking representations for sensitive values."""

    @classmethod
    def mask(cls, entity_type: PIIEntityType, value: str) -> str:
        if not value:
            return ""

        val = value.strip()

        if entity_type == PIIEntityType.EMAIL:
            if "@" in val:
                user, domain = val.split("@", 1)
                if len(user) <= 1:
                    masked_user = "*"
                else:
                    masked_user = user[0] + "***"
                return f"{masked_user}@{domain}"
            return val[0] + "***"

        if entity_type == PIIEntityType.PHONE_NUMBER:
            digits = re.sub(r"\D", "", val)
            if len(digits) >= 10:
                return f"{digits[:2]}******{digits[-2:]}"
            elif len(val) >= 4:
                return f"{val[:2]}****{val[-2:]}"
            return "****"

        if entity_type == PIIEntityType.CREDIT_CARD:
            digits = re.sub(r"\D", "", val)
            if len(digits) >= 12:
                return f"{digits[:4]}{'*' * (len(digits) - 4)}"
            return "****"

        if entity_type in (
            PIIEntityType.OPENAI_API_KEY,
            PIIEntityType.AWS_ACCESS_KEY,
            PIIEntityType.GITHUB_TOKEN,
            PIIEntityType.GOOGLE_API_KEY,
            PIIEntityType.JWT_TOKEN,
            PIIEntityType.BEARER_TOKEN,
            PIIEntityType.API_KEY_GENERIC,
            PIIEntityType.GENERIC_SECRET,
            PIIEntityType.URL_ACCESS_TOKEN,
        ):
            if val.startswith("sk-") or val.startswith("AKIA") or val.startswith("ghp_"):
                prefix = val[:3]
                return f"{prefix}-************"
            if len(val) > 6:
                return f"{val[:3]}************"
            return "************"

        if entity_type == PIIEntityType.US_SSN:
            parts = val.split("-")
            if len(parts) == 3:
                return f"***-**-{parts[2]}"
            return f"***-**-{val[-4:]}"

        if entity_type == PIIEntityType.IN_AADHAAR:
            digits = re.sub(r"\D", "", val)
            if len(digits) == 12:
                return f"**** **** {digits[-4:]}"
            return "**** **** ****"

        if entity_type == PIIEntityType.IN_PAN:
            if len(val) == 10:
                return f"{val[:2]}*****{val[-2:]}"
            return "AB*****34F"

        if entity_type == PIIEntityType.IPV4_ADDRESS:
            parts = val.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.*.*"
            return "*.*.*.*"

        if entity_type == PIIEntityType.IPV6_ADDRESS:
            parts = val.split(":")
            if len(parts) >= 2:
                return f"{parts[0]}:****:*:*"
            return "*:*:*:*"

        # General Fallback Masking
        if len(val) > 4:
            return f"{val[0]}{'*' * (len(val) - 2)}{val[-1]}"
        return "*" * len(val)


class PIIRule(BaseModel):
    """Configurable rule definition model for PII entity detection."""

    rule_id: str = Field(..., description="Unique rule identifier code (e.g. PII-001)")
    entity_type: PIIEntityType = Field(..., description="Target entity type classification")
    pattern: str = Field(..., description="Regex pattern string for matching")
    severity: DetectorSeverity = Field(
        default=DetectorSeverity.MEDIUM, description="Severity classification"
    )
    risk_weight: float = Field(
        default=25.0, ge=0.0, le=100.0, description="Risk penalty weight applied when matched"
    )
    confidence: float = Field(
        default=0.90, ge=0.0, le=1.0, description="Baseline confidence score"
    )
    description: str = Field(..., description="Detailed description of entity threat")
    remediation: str = Field(
        default="Redact or mask PII entity before processing.",
        description="Remediation guidance",
    )


DEFAULT_PII_RULES: List[PIIRule] = [
    PIIRule(
        rule_id="PII-EMAIL",
        entity_type=PIIEntityType.EMAIL,
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        severity=DetectorSeverity.MEDIUM,
        risk_weight=15.0,
        confidence=0.95,
        description="Email address detected in prompt.",
        remediation="Mask email address to protect user PII.",
    ),
    PIIRule(
        rule_id="PII-PHONE",
        entity_type=PIIEntityType.PHONE_NUMBER,
        pattern=r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b[6-9]\d{9}\b",
        severity=DetectorSeverity.MEDIUM,
        risk_weight=15.0,
        confidence=0.90,
        description="Phone number detected in prompt.",
        remediation="Mask phone number before passing text downstream.",
    ),
    PIIRule(
        rule_id="PII-CREDIT-CARD",
        entity_type=PIIEntityType.CREDIT_CARD,
        pattern=r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b|\b(?:\d{4}[-\s]?){3}\d{4}\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=40.0,
        confidence=0.95,
        description="Credit Card number detected in prompt.",
        remediation="Redact financial credit card details immediately.",
    ),
    PIIRule(
        rule_id="PII-IPV4",
        entity_type=PIIEntityType.IPV4_ADDRESS,
        pattern=r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        severity=DetectorSeverity.MEDIUM,
        risk_weight=10.0,
        confidence=0.90,
        description="IPv4 address detected.",
        remediation="Mask infrastructure network IP addresses.",
    ),
    PIIRule(
        rule_id="PII-IPV6",
        entity_type=PIIEntityType.IPV6_ADDRESS,
        pattern=r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",
        severity=DetectorSeverity.MEDIUM,
        risk_weight=10.0,
        confidence=0.90,
        description="IPv6 address detected.",
        remediation="Mask IPv6 infrastructure network address.",
    ),
    PIIRule(
        rule_id="PII-OPENAI-KEY",
        entity_type=PIIEntityType.OPENAI_API_KEY,
        pattern=r"\bsk-(?:proj-|admin-|svcacct-)?[A-Za-z0-9_-]{20,}\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=50.0,
        confidence=0.98,
        description="OpenAI API key detected in prompt.",
        remediation="Revoke exposed API key and purge from input.",
    ),
    PIIRule(
        rule_id="PII-AWS-KEY",
        entity_type=PIIEntityType.AWS_ACCESS_KEY,
        pattern=r"\b(AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=50.0,
        confidence=0.98,
        description="AWS Access Key ID detected.",
        remediation="Revoke exposed AWS credentials immediately.",
    ),
    PIIRule(
        rule_id="PII-GITHUB-TOKEN",
        entity_type=PIIEntityType.GITHUB_TOKEN,
        pattern=r"\b(ghp|gho|ghu|ghs|r8)_[A-Za-z0-9_]{36,}\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=50.0,
        confidence=0.98,
        description="GitHub Personal Access Token detected.",
        remediation="Revoke GitHub token and restrict repository access.",
    ),
    PIIRule(
        rule_id="PII-GOOGLE-KEY",
        entity_type=PIIEntityType.GOOGLE_API_KEY,
        pattern=r"\bAIzaSy[A-Za-z0-9_-]{33}\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=50.0,
        confidence=0.98,
        description="Google API Key detected.",
        remediation="Revoke Google Cloud API key.",
    ),
    PIIRule(
        rule_id="PII-JWT",
        entity_type=PIIEntityType.JWT_TOKEN,
        pattern=r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=45.0,
        confidence=0.95,
        description="JSON Web Token (JWT) authorization credential detected.",
        remediation="Block JWT credentials from prompt payload.",
    ),
    PIIRule(
        rule_id="PII-BEARER-TOKEN",
        entity_type=PIIEntityType.BEARER_TOKEN,
        pattern=r"\bBearer\s+[A-Za-z0-9\-._~+/]+=*\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=45.0,
        confidence=0.95,
        description="HTTP Bearer authentication token detected.",
        remediation="Strip Bearer tokens from user prompts.",
    ),
    PIIRule(
        rule_id="PII-API-KEY-GENERIC",
        entity_type=PIIEntityType.API_KEY_GENERIC,
        pattern=r"\b(?:api[_-]?key|secret[_-]?key|auth[_-]?token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})['\"]?\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=45.0,
        confidence=0.92,
        description="Generic API Key assignment pattern detected.",
        remediation="Redact secret assignment values.",
    ),
    PIIRule(
        rule_id="PII-GENERIC-SECRET",
        entity_type=PIIEntityType.GENERIC_SECRET,
        pattern=r"\b(?:password|passwd|pwd|private[_-]?key)\s*[:=]\s*['\"]?([^\s'\"]{6,})['\"]?\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=45.0,
        confidence=0.90,
        description="Password or secret assignment detected.",
        remediation="Redact confidential credentials.",
    ),
    PIIRule(
        rule_id="PII-US-SSN",
        entity_type=PIIEntityType.US_SSN,
        pattern=r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=40.0,
        confidence=0.92,
        description="US Social Security Number (SSN) detected.",
        remediation="Redact SSN government identity number.",
    ),
    PIIRule(
        rule_id="PII-IN-AADHAAR",
        entity_type=PIIEntityType.IN_AADHAAR,
        pattern=r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=40.0,
        confidence=0.88,
        description="India Aadhaar national identity number detected.",
        remediation="Redact Aadhaar identity details.",
    ),
    PIIRule(
        rule_id="PII-IN-PAN",
        entity_type=PIIEntityType.IN_PAN,
        pattern=r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=40.0,
        confidence=0.95,
        description="India Permanent Account Number (PAN) tax ID detected.",
        remediation="Mask PAN financial identity number.",
    ),
    PIIRule(
        rule_id="PII-PASSPORT",
        entity_type=PIIEntityType.PASSPORT_NUMBER,
        pattern=r"\b[A-PR-WYa-pr-wy][0-9]{7}\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        confidence=0.85,
        description="Passport document number detected.",
        remediation="Redact passport travel identity details.",
    ),
    PIIRule(
        rule_id="PII-BANK-ACCOUNT",
        entity_type=PIIEntityType.BANK_ACCOUNT,
        pattern=r"\b(?:account|iban|acc)[#:\s]*[0-9]{8,18}\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        confidence=0.85,
        description="Bank account number pattern detected.",
        remediation="Redact bank account numbers.",
    ),
    PIIRule(
        rule_id="PII-URL-TOKEN",
        entity_type=PIIEntityType.URL_ACCESS_TOKEN,
        pattern=r"https?://[^\s]+\?(?:[^\s]*&)?(?:access_token|api_key|token|auth)=([A-Za-z0-9_\-]{8,})",
        severity=DetectorSeverity.LOW,
        risk_weight=20.0,
        confidence=0.90,
        description="URL containing access token parameter detected.",
        remediation="Strip query token parameters from URLs.",
    ),
]


class PIIMatch(BaseModel):
    """DTO representing a detected PII entity match."""

    rule_id: str
    entity_type: PIIEntityType
    matched_value: str
    masked_value: str
    start_position: int
    end_position: int
    severity: DetectorSeverity
    confidence: float
    risk_weight: float
    description: str
    remediation: str


def _luhn_check(card_number: str) -> bool:
    """Luhn Algorithm validation helper to verify valid credit card numbers."""
    digits = [int(c) for c in re.sub(r"\D", "", card_number)]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


class PIIRuleEngine:
    """Rule engine component evaluating regex PII rules against prompt text."""

    def __init__(self, rules: Optional[List[PIIRule]] = None) -> None:
        self.rules: List[PIIRule] = rules if rules is not None else DEFAULT_PII_RULES
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._compile_rules()

    def _compile_rules(self) -> None:
        self._compiled_patterns.clear()
        for rule in self.rules:
            try:
                self._compiled_patterns[rule.rule_id] = re.compile(rule.pattern)
            except re.error as err:
                logger.error(f"Failed to compile PII regex for rule {rule.rule_id}: {err}")

    def evaluate(self, text: str) -> List[PIIMatch]:
        matches: List[PIIMatch] = []
        if not text:
            return matches

        for rule in self.rules:
            pattern = self._compiled_patterns.get(rule.rule_id)
            if not pattern:
                continue

            for match in pattern.finditer(text):
                matched_val = match.group(0)

                # Secondary validation: Luhn check for credit cards
                if rule.entity_type == PIIEntityType.CREDIT_CARD:
                    if not _luhn_check(matched_val):
                        continue

                masked_val = PIIMasker.mask(rule.entity_type, matched_val)
                matches.append(
                    PIIMatch(
                        rule_id=rule.rule_id,
                        entity_type=rule.entity_type,
                        matched_value=matched_val,
                        masked_value=masked_val,
                        start_position=match.start(),
                        end_position=match.end(),
                        severity=rule.severity,
                        confidence=rule.confidence,
                        risk_weight=rule.risk_weight,
                        description=rule.description,
                        remediation=rule.remediation,
                    )
                )

        return matches


class PIIDetector(BaseDetector):
    """
    Production-ready offline Personally Identifiable Information (PII) Detector.
    
    Identifies sensitive personal information, credentials, financial details,
    and government identifiers in input prompts and generates masked representations.
    """

    def __init__(self, rule_engine: Optional[PIIRuleEngine] = None) -> None:
        self.rule_engine = rule_engine or PIIRuleEngine()

    @property
    def name(self) -> str:
        return "pii_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        start_time = time.perf_counter()

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

        matches = self.rule_engine.evaluate(prompt)
        is_triggered = len(matches) > 0

        total_penalty = sum(m.risk_weight for m in matches)
        calculated_score = round(max(0.0, min(100.0, 100.0 - total_penalty)), 2)

        findings: List[FindingDetail] = []
        for m in matches:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category=f"pii.{m.entity_type.value.lower()}",
                    severity=m.severity,
                    description=f"{m.description} Masked: {m.masked_value}",
                    confidence_score=m.confidence,
                    metadata={
                        "entity_type": m.entity_type.value,
                        "matched_value": m.matched_value,
                        "masked_value": m.masked_value,
                        "start_position": m.start_position,
                        "end_position": m.end_position,
                        "rule_id": m.rule_id,
                        "remediation": m.remediation,
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
                "pii_entities_detected": len(matches),
                "entity_types": list({m.entity_type.value for m in matches}),
            },
        )

import re
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from shared.logger import get_logger
from shared.interfaces import BaseDetector, DetectorResult, DetectorSeverity, FindingDetail

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

import re
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from shared.logger import get_logger
from shared.interfaces import BaseDetector, DetectorResult, DetectorSeverity, FindingDetail

logger = get_logger(__name__)


class ToxicityCategory(str, Enum):
    """Supported Toxicity Classifications."""

    PROFANITY = "PROFANITY"
    INSULT = "INSULT"
    HARASSMENT = "HARASSMENT"
    HATE_SPEECH = "HATE_SPEECH"
    THREAT = "THREAT"
    VIOLENCE = "VIOLENCE"
    SEXUAL_CONTENT = "SEXUAL_CONTENT"
    SELF_HARM = "SELF_HARM"
    DISCRIMINATION = "DISCRIMINATION"
    CYBERBULLYING = "CYBERBULLYING"


class NormalizedToxicityPrompt(BaseModel):
    """Normalized prompt model for toxicity evaluation."""

    original_prompt: str
    normalized_text: str
    deobfuscated_text: str
    char_count: int
    word_count: int
    uppercase_ratio: float


class ToxicityNormalizer:
    """Utility class for de-obfuscating leetspeak, collapsing repeated chars, and normalizing text."""

    LEET_MAP = {
        "@": "a",
        "$": "s",
        "0": "o",
        "1": "i",
        "!": "i",
        "3": "e",
        "5": "s",
        "7": "t",
        "8": "b",
    }

    @classmethod
    def normalize(cls, prompt: str) -> NormalizedToxicityPrompt:
        original = prompt or ""
        clean_spaces = re.sub(r"\s+", " ", original).strip()
        lower_text = clean_spaces.lower()

        # Calculate uppercase ratio on original non-whitespace chars
        non_space_chars = [c for c in original if not c.isspace()]
        upper_chars = [c for c in non_space_chars if c.isupper()]
        uppercase_ratio = (
            round(len(upper_chars) / len(non_space_chars), 3) if non_space_chars else 0.0
        )

        # De-obfuscate leetspeak
        deobfuscated = lower_text
        for leet, replacement in cls.LEET_MAP.items():
            deobfuscated = deobfuscated.replace(leet, replacement)

        # Collapse repeated characters (3+ consecutive identical chars -> 1)
        deobfuscated = re.sub(r"(.)\1{2,}", r"\1", deobfuscated)

        words = [w for w in deobfuscated.split(" ") if w]

        return NormalizedToxicityPrompt(
            original_prompt=original,
            normalized_text=lower_text,
            deobfuscated_text=deobfuscated,
            char_count=len(original),
            word_count=len(words),
            uppercase_ratio=uppercase_ratio,
        )


class ToxicityRule(BaseModel):
    """Rule definition model for offline toxicity detection."""

    rule_id: str = Field(..., description="Unique rule identifier (e.g. TOX-THREAT-01)")
    category: ToxicityCategory = Field(..., description="Target toxicity category")
    pattern: str = Field(..., description="Regex pattern for matching")
    severity: DetectorSeverity = Field(
        default=DetectorSeverity.HIGH, description="Severity classification"
    )
    risk_weight: float = Field(
        default=30.0, ge=0.0, le=100.0, description="Risk penalty weight applied when matched"
    )
    confidence: float = Field(
        default=0.95, ge=0.0, le=1.0, description="Confidence score"
    )
    description: str = Field(..., description="Description of detected threat")
    remediation: str = Field(
        default="Filter or redact toxic content before downstream processing.",
        description="Remediation guidance",
    )


DEFAULT_TOXICITY_RULES: List[ToxicityRule] = [
    # 1. Self-Harm
    ToxicityRule(
        rule_id="TOX-SELFHARM-01",
        category=ToxicityCategory.SELF_HARM,
        pattern=r"\b(kill|end|cut|hang|harm)\s+(your\s*self|my\s*self)\b|\b(suicide|suicidal|want to die|how to die)\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=50.0,
        confidence=0.98,
        description="Encouragement or statements regarding suicide or self-harm detected.",
        remediation="Block self-harm references immediately and provide crisis hotline support.",
    ),
    # 2. Threat
    ToxicityRule(
        rule_id="TOX-THREAT-01",
        category=ToxicityCategory.THREAT,
        pattern=r"\b(i\s+will|going\s+to|gonna)\s+(kill|murder|stab|shoot|destroy|hunt|behead|torture)\s+(you|them|him|her)\b|\b(death\s+threat|kill\s+you)\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=50.0,
        confidence=0.98,
        description="Explicit physical threat or intent to murder/harm detected.",
        remediation="Block threat payload and flag for safety audit.",
    ),
    # 3. Hate Speech
    ToxicityRule(
        rule_id="TOX-HATE-01",
        category=ToxicityCategory.HATE_SPEECH,
        pattern=r"\b(nigger|nigga|faggot|kike|chink|spic|retard|wetback|towelhead)\b|\b(hate\s+(all\s+)?(jews|blacks|whites|muslims|gays|trans|foreigners))\b",
        severity=DetectorSeverity.CRITICAL,
        risk_weight=45.0,
        confidence=0.98,
        description="Hate speech slur or group attack detected.",
        remediation="Sanitize hate speech slurs and block discriminatory attacks.",
    ),
    # 4. Violence
    ToxicityRule(
        rule_id="TOX-VIOLENCE-01",
        category=ToxicityCategory.VIOLENCE,
        pattern=r"\b(bloodbath|massacre|decapitate|mutilate|slaughter|decapitation|dismember)\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=40.0,
        confidence=0.92,
        description="Graphic violent language or violent acts description detected.",
        remediation="Filter graphic violent descriptions.",
    ),
    # 5. Cyberbullying & Doxxing
    ToxicityRule(
        rule_id="TOX-CYBERBULLY-01",
        category=ToxicityCategory.CYBERBULLYING,
        pattern=r"\b(dox|doxx|doxxing)\s+(them|him|her|this\s+person)\b|\b(expose|publish)\s+(their|his|her)\s+(address|ssn|home|family|phone)\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        confidence=0.92,
        description="Doxxing or cyberbullying target campaign detected.",
        remediation="Reject doxxing threats and targeted public exposure prompts.",
    ),
    # 6. Harassment
    ToxicityRule(
        rule_id="TOX-HARASS-01",
        category=ToxicityCategory.HARASSMENT,
        pattern=r"\b(stalking|harass|harassing|nobody\s+likes\s+you|go\s+die|you\s+should\s+die)\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        confidence=0.90,
        description="Targeted harassment phrasing detected.",
        remediation="Block intimidation and persistent harassment prompts.",
    ),
    # 7. Sexual Content
    ToxicityRule(
        rule_id="TOX-SEXUAL-01",
        category=ToxicityCategory.SEXUAL_CONTENT,
        pattern=r"\b(porn|pornography|explicit\s+sex|nude\s+pics|send\s+nudes|non-consensual\s+sexual)\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        confidence=0.90,
        description="Explicit or non-consensual sexual content detected.",
        remediation="Redact explicit sexual material.",
    ),
    # 8. Discrimination
    ToxicityRule(
        rule_id="TOX-DISCRIM-01",
        category=ToxicityCategory.DISCRIMINATION,
        pattern=r"\b(inferior\s+race|subhuman\s+race|discriminate\s+against|racial\s+purity)\b",
        severity=DetectorSeverity.HIGH,
        risk_weight=35.0,
        confidence=0.90,
        description="Discriminatory or bigoted language detected.",
        remediation="Reject discriminatory and exclusionary content.",
    ),
    # 9. Insult
    ToxicityRule(
        rule_id="TOX-INSULT-01",
        category=ToxicityCategory.INSULT,
        pattern=r"\b(you\s+are\s+an?\s+)?(idiot|moron|dumbass|stupid|loser|bastard|jackass|jerk|fool)\b",
        severity=DetectorSeverity.MEDIUM,
        risk_weight=20.0,
        confidence=0.88,
        description="Personal insult or derogatory name-calling detected.",
        remediation="Flag personal derogatory insults.",
    ),
    # 10. Profanity
    ToxicityRule(
        rule_id="TOX-PROFANE-01",
        category=ToxicityCategory.PROFANITY,
        pattern=r"\b(fuck|shit|bitch|asshole|cunt|dick|pussy|bastard|bullshit)\b",
        severity=DetectorSeverity.LOW,
        risk_weight=15.0,
        confidence=0.95,
        description="Vulgar profanity detected.",
        remediation="Mask or filter expletives and vulgar language.",
    ),
]


class ToxicityMatch(BaseModel):
    """DTO representing a matched toxicity rule instance."""

    rule_id: str
    category: ToxicityCategory
    severity: DetectorSeverity
    risk_weight: float
    confidence: float
    matched_text: str
    description: str
    remediation: str


class ToxicityRuleEngine:
    """Offline rule engine evaluating compiled regex rules against normalized prompts."""

    def __init__(self, rules: Optional[List[ToxicityRule]] = None) -> None:
        self.rules: List[ToxicityRule] = rules if rules is not None else DEFAULT_TOXICITY_RULES
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._compile_rules()

    def _compile_rules(self) -> None:
        self._compiled_patterns.clear()
        for rule in self.rules:
            try:
                self._compiled_patterns[rule.rule_id] = re.compile(rule.pattern, re.IGNORECASE)
            except re.error as err:
                logger.error(f"Failed to compile toxicity regex for rule {rule.rule_id}: {err}")

    def evaluate(self, normalized: NormalizedToxicityPrompt) -> List[ToxicityMatch]:
        matches: List[ToxicityMatch] = []
        if not normalized.deobfuscated_text:
            return matches

        for rule in self.rules:
            pattern = self._compiled_patterns.get(rule.rule_id)
            if not pattern:
                continue

            match = pattern.search(normalized.deobfuscated_text)
            if match:
                matches.append(
                    ToxicityMatch(
                        rule_id=rule.rule_id,
                        category=rule.category,
                        severity=rule.severity,
                        risk_weight=rule.risk_weight,
                        confidence=rule.confidence,
                        matched_text=match.group(0),
                        description=rule.description,
                        remediation=rule.remediation,
                    )
                )

        return matches


class ToxicityHeuristicScore(BaseModel):
    """DTO representing structural heuristic analysis outputs."""

    penalty_score: float
    uppercase_ratio: float
    signals: List[str]


class ToxicityHeuristics:
    """Heuristic structural analyzer evaluating shouting density and aggressive punctuation abuse."""

    def evaluate(self, normalized: NormalizedToxicityPrompt) -> ToxicityHeuristicScore:
        signals: List[str] = []
        penalty = 0.0

        # Detect ALL-CAPS shouting aggression (>60% uppercase on prompts > 10 chars)
        if normalized.uppercase_ratio > 0.60 and normalized.char_count > 10:
            penalty += 15.0
            signals.append(
                f"Aggressive ALL-CAPS shouting detected ({normalized.uppercase_ratio * 100:.1f}% uppercase)"
            )

        # Detect excessive aggressive punctuation abuse (e.g. "!!!" or "???")
        punct_count = normalized.original_prompt.count("!") + normalized.original_prompt.count("?")
        if punct_count >= 4 and normalized.word_count < 10:
            penalty += 10.0
            signals.append("Aggressive punctuation abuse detected")

        return ToxicityHeuristicScore(
            penalty_score=min(penalty, 30.0),
            uppercase_ratio=normalized.uppercase_ratio,
            signals=signals,
        )


class ToxicityDetector(BaseDetector):
    """
    Production-ready offline Toxicity Detection Engine.
    
    Identifies toxic content, threats, profanity, hate speech, harassment, self-harm,
    and cyberbullying using a 100% offline normalizer, regex engine, and heuristic analyzer.
    """

    def __init__(
        self,
        rule_engine: Optional[ToxicityRuleEngine] = None,
        heuristics: Optional[ToxicityHeuristics] = None,
    ) -> None:
        self.rule_engine = rule_engine or ToxicityRuleEngine()
        self.heuristics = heuristics or ToxicityHeuristics()

    @property
    def name(self) -> str:
        return "toxicity_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        start_time = time.perf_counter()

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

        # Step 1: Input Normalization & De-obfuscation
        normalized = ToxicityNormalizer.normalize(prompt)

        # Step 2: Rule Engine Evaluation
        rule_matches = self.rule_engine.evaluate(normalized)

        # Step 3: Heuristic Evaluation
        heuristic_res = self.heuristics.evaluate(normalized)

        # Step 4: Risk Penalty Calculation
        rule_penalty = sum(m.risk_weight for m in rule_matches)
        total_penalty = rule_penalty + heuristic_res.penalty_score
        calculated_score = round(max(0.0, min(100.0, 100.0 - total_penalty)), 2)

        is_triggered = len(rule_matches) > 0 or heuristic_res.penalty_score >= 15.0

        # Step 5: Finding Generation
        findings: List[FindingDetail] = []
        for match in rule_matches:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category=f"toxicity.{match.category.value.lower()}",
                    severity=match.severity,
                    description=f"Rule [{match.rule_id}] Triggered: {match.description}",
                    confidence_score=match.confidence,
                    metadata={
                        "rule_id": match.rule_id,
                        "category_enum": match.category.value,
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
                    category="toxicity.heuristic_aggression",
                    severity=DetectorSeverity.MEDIUM,
                    description=f"Heuristic text aggression detected: {'; '.join(heuristic_res.signals)}",
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
                "toxic_categories_detected": list({m.category.value for m in rule_matches}),
                "heuristic_penalty": heuristic_res.penalty_score,
            },
        )

import re
import time
from typing import Any, Dict, List

from shared.interfaces import BaseDetector, DetectorResult, DetectorSeverity, FindingDetail
from shared.logger import get_logger

logger = get_logger(__name__)


class HallucinationDetector(BaseDetector):
    """
    Offline, heuristic-based hallucination detection engine.
    Detects fabricated references, impossible dates, unfulfilled placeholders,
    unsupported claims, and basic contradictions.
    """

    @property
    def name(self) -> str:
        return "hallucination_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    def _detect_impossible_dates(self, text: str) -> List[FindingDetail]:
        findings = []
        # Basic heuristic for dates like February 30th or 31st
        feb_invalid = re.search(r'(?i)february\s+(30|31)(?:st|th)?', text)
        if feb_invalid:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="hallucination.impossible_date",
                    severity=DetectorSeverity.HIGH,
                    description=f"Found impossible date: {feb_invalid.group(0)}",
                    confidence_score=1.0,
                )
            )

        # Dates like April 31st, June 31st, Sept 31st, Nov 31st
        apr_jun_sep_nov_invalid = re.search(r'(?i)(april|june|september|november)\s+31(?:st)?', text)
        if apr_jun_sep_nov_invalid:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="hallucination.impossible_date",
                    severity=DetectorSeverity.HIGH,
                    description=f"Found impossible date: {apr_jun_sep_nov_invalid.group(0)}",
                    confidence_score=1.0,
                )
            )

        # Extreme future dates presented as historical fact (e.g. 2050+)
        # For simplicity, we just flag mentions of very distant years in "In the year XXXX" format
        distant_future = re.search(r'(?i)(in the year\s+|by the year\s+|dated\s+)(2[1-9]\d{2}|[3-9]\d{3})', text)
        if distant_future:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="hallucination.impossible_date",
                    severity=DetectorSeverity.MEDIUM,
                    description=f"Found suspicious distant future date: {distant_future.group(0)}",
                    confidence_score=0.8,
                )
            )
        return findings

    def _detect_fake_citations(self, text: str) -> List[FindingDetail]:
        findings = []
        # Catch structurally invalid DOIs (DOI format is typically 10.XXXX/... )
        invalid_doi = re.search(r'(?i)doi:\s*(10\.\d+/(?:fake|invalid|xxx+))', text)
        if invalid_doi:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="hallucination.fake_citation",
                    severity=DetectorSeverity.HIGH,
                    description=f"Suspicious or invalid DOI detected: {invalid_doi.group(0)}",
                    confidence_score=0.9,
                )
            )

        # Invalid IP addresses mapping to outside 0-255 range
        invalid_ip = re.search(r'\b(?:25[6-9]|2[6-9]\d|[3-9]\d{2})\.\d+\.\d+\.\d+\b', text)
        if invalid_ip:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="hallucination.fake_citation",
                    severity=DetectorSeverity.HIGH,
                    description=f"Invalid IP address detected: {invalid_ip.group(0)}",
                    confidence_score=1.0,
                )
            )

        # Very generic fake domains
        fake_domain = re.search(r'(?i)(example\.com|fakeurl\.com|wikipedia\.org/wiki/Fake_Page)', text)
        if fake_domain:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="hallucination.fake_citation",
                    severity=DetectorSeverity.MEDIUM,
                    description=f"Placeholder or known fake domain used as citation: {fake_domain.group(0)}",
                    confidence_score=0.8,
                )
            )

        return findings

    def _detect_placeholders(self, text: str) -> List[FindingDetail]:
        findings = []
        # Unfulfilled placeholders commonly left by LLMs
        placeholder_pattern = re.search(r'(?i)\[insert (?:link|citation|date|name)(?: here)?\]|<TODO>|XX-XXXX|XXXX-XXXX-XXXX', text)
        if placeholder_pattern:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="hallucination.placeholder",
                    severity=DetectorSeverity.MEDIUM,
                    description=f"Unfulfilled placeholder detected: {placeholder_pattern.group(0)}",
                    confidence_score=0.9,
                )
            )
        return findings

    def _detect_unsupported_claims(self, text: str) -> List[FindingDetail]:
        findings = []
        # Overconfident absolutes commonly used when hallucinating without evidence
        claim_pattern = re.search(
            r'(?i)(there is absolutely zero evidence that|it is an undisputed fact that|research definitively proves|studies prove that)', 
            text
        )
        if claim_pattern:
            findings.append(
                FindingDetail(
                    detector_name=self.name,
                    category="hallucination.unsupported_claim",
                    severity=DetectorSeverity.LOW,
                    description=f"Overconfident but unsubstantiated phrase detected: {claim_pattern.group(0)}",
                    confidence_score=0.6,
                )
            )
        return findings

    def _detect_contradictions(self, text: str) -> List[FindingDetail]:
        findings = []
        # Basic structural contradiction markers
        # E.g., starting with "I cannot answer that" but providing an answer below
        if re.search(r'(?i)(i cannot answer that|as an ai language model, i cannot)', text):
            # Check if text continues significantly (more than 50 chars) after refusing
            if len(text) > 100:
                findings.append(
                    FindingDetail(
                        detector_name=self.name,
                        category="hallucination.contradiction",
                        severity=DetectorSeverity.MEDIUM,
                        description="Possible contradiction: text refuses to answer but provides a detailed response.",
                        confidence_score=0.7,
                    )
                )
        return findings

    async def analyze(self, prompt: str, metadata: Dict[str, Any] | None = None) -> DetectorResult:
        start_time = time.perf_counter()
        findings: List[FindingDetail] = []

        findings.extend(self._detect_impossible_dates(prompt))
        findings.extend(self._detect_fake_citations(prompt))
        findings.extend(self._detect_placeholders(prompt))
        findings.extend(self._detect_unsupported_claims(prompt))
        findings.extend(self._detect_contradictions(prompt))

        # We can implement a basic scoring logic if we have findings.
        # But for now, we just pass findings. The TrustScoreEngine handles the score calculation.
        # BaseDetector expects a score. We can calculate a naive score like 100 - (findings * 10)
        # However, the orchestrator only uses the findings to pass into TrustScoreEngine.
        is_triggered = len(findings) > 0
        score = 100.0 - (len(findings) * 10.0)
        score = max(0.0, score)

        execution_time_ms = (time.perf_counter() - start_time) * 1000

        return DetectorResult(
            detector_name=self.name,
            is_triggered=is_triggered,
            score=score,
            findings=findings,
            execution_time_ms=execution_time_ms,
        )
import re
import time
from typing import Any, Dict, List

from shared.interfaces import BaseDetector, DetectorResult, DetectorSeverity, FindingDetail
from shared.logger import get_logger

logger = get_logger(__name__)


class BiasDetector(BaseDetector):
    """
    Offline, heuristic-based Bias & Fairness detection engine.
    Detects discriminatory language, occupational stereotypes, and harmful traits 
    associated with protected characteristics using proximity matching.
    """

    def __init__(self) -> None:
        super().__init__()
        # 1. Protected Attribute Taxonomies
        self.taxonomies = {
            "gender": r"\b(women|men|woman|man|girls|boys|transgender|non-binary|females|males)\b",
            "race_ethnicity": r"\b(black|white|asian|hispanic|latino|latina|indigenous|native)\b",
            "religion": r"\b(muslim|christian|jewish|hindu|buddhist|sikh)\b",
            "age": r"\b(elderly|boomer|millennial|teenager|old people|young people)\b",
            "disability": r"\b(disabled|autistic|blind|deaf|wheelchair)\b",
        }

        # 2. Harmful Stereotypes / Modifiers
        self.negative_traits = r"\b(lazy|violent|greedy|weak|stupid|dumb|dangerous|terrorist|criminal|inferior|bossy)\b"
        self.occupational_exclusion = r"\b(cannot be a|shouldn't be a|should not work as|cannot work as|bad at math|bad at driving|bad at science)\b"

        # 3. False Positive Reducers (Neutral / Academic Contexts)
        self.academic_context = r"\b(study|research|historical context|demographics|paper|academic|survey|analysis)\b"

    @property
    def name(self) -> str:
        return "bias_detector"

    @property
    def version(self) -> str:
        return "1.0.0"

    def _is_academic_context(self, text: str) -> bool:
        """
        Checks if the text appears to be discussing the topic in an academic or neutral setting.
        """
        return bool(re.search(self.academic_context, text, re.IGNORECASE))

    def _detect_stereotypes_and_traits(self, text: str, is_academic: bool) -> List[FindingDetail]:
        findings = []

        # If it's an academic context, we might skip the low-confidence heuristic matching entirely,
        # or we could apply it but with a reduced severity. For this rule-based system, we will 
        # completely suppress negative trait matching in academic context to avoid massive false positives.
        if is_academic:
            return findings

        # Iterate over all taxonomies and look for proximity to negative traits or occupational exclusions
        for attr_category, attr_regex in self.taxonomies.items():
            # Check for occupational exclusion
            # E.g., "women cannot be a..." or "...cannot be a woman"
            # We use a broad window of up to 40 characters between the term and the exclusion phrase
            exclusion_pattern = re.compile(
                f"({attr_regex}.{{0,40}}{self.occupational_exclusion})|({self.occupational_exclusion}.{{0,40}}{attr_regex})",
                re.IGNORECASE
            )
            
            for match in exclusion_pattern.finditer(text):
                findings.append(
                    FindingDetail(
                        detector_name=self.name,
                        category=f"bias.{attr_category}",
                        severity=DetectorSeverity.HIGH,
                        description=f"Occupational stereotype or exclusion detected targeting {attr_category}.",
                        confidence_score=0.9,
                    )
                )

            # Check for negative traits proximity
            trait_pattern = re.compile(
                f"({attr_regex}.{{0,30}}{self.negative_traits})|({self.negative_traits}.{{0,30}}{attr_regex})",
                re.IGNORECASE
            )
            
            for match in trait_pattern.finditer(text):
                findings.append(
                    FindingDetail(
                        detector_name=self.name,
                        category=f"bias.{attr_category}",
                        severity=DetectorSeverity.MEDIUM,
                        description=f"Derogatory or stereotyping trait associated with {attr_category}.",
                        confidence_score=0.7,
                    )
                )

        return findings

    async def analyze(self, prompt: str, metadata: Dict[str, Any] | None = None) -> DetectorResult:
        start_time = time.perf_counter()
        findings: List[FindingDetail] = []

        is_academic = self._is_academic_context(prompt)
        findings.extend(self._detect_stereotypes_and_traits(prompt, is_academic))

        # Deduplicate findings if a match hit multiple times
        dedup_findings = []
        seen = set()
        for f in findings:
            key = (f.category, f.severity.value, f.description)
            if key not in seen:
                seen.add(key)
                dedup_findings.append(f)

        is_triggered = len(dedup_findings) > 0
        
        # Simple local score calculation
        score = 100.0
        if is_triggered:
            score = max(0.0, 100.0 - (len(dedup_findings) * 15.0))

        execution_time_ms = (time.perf_counter() - start_time) * 1000

        return DetectorResult(
            detector_name=self.name,
            is_triggered=is_triggered,
            score=score,
            findings=dedup_findings,
            execution_time_ms=execution_time_ms,
        )
