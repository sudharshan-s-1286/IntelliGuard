import re
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.detectors.base import BaseDetector, DetectorResult, DetectorSeverity, FindingDetail

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
