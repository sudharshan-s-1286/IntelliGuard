"""Domain models for the Privacy Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .constants import DEFAULT_RISK_SCORE_CAP
from .exceptions import ClassificationError


class EntityCategory(str, Enum):
    """Categories of PII entities."""

    IDENTIFYING = "identifying"
    FINANCIAL = "financial"
    CONTACT = "contact"
    GOVERNMENT = "government"
    MEDICAL = "medical"
    DEMOGRAPHIC = "demographic"


class EntityType(str, Enum):
    """Supported PII entity types."""

    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    MEDICAL_RECORD = "medical_record"
    FINANCIAL_ACCOUNT = "financial_account"


@dataclass(frozen=True)
class PIIEntity:
    """Immutable representation of a detected PII entity."""

    entity_type: str
    value: str
    start: int
    end: int
    confidence: float
    sensitivity: str
    context: str

    def __post_init__(self) -> None:
        """Validate entity invariants after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            msg: str = (
                f"Confidence must be between 0.0 and 1.0,"
                f" got {self.confidence}"
            )
            raise ClassificationError(msg)
        if self.start < 0 or self.end < 0:
            msg: str = "Start and end offsets must be non-negative"
            raise ClassificationError(msg)
        if self.end < self.start:
            msg: str = (
                "End offset must be greater than or equal"
                " to start offset"
            )
            raise ClassificationError(msg)

    @property
    def length(self) -> int:
        """Return the length of the detected entity value."""
        return self.end - self.start


@dataclass(frozen=True)
class PrivacyFinding:
    """Immutable representation of a privacy finding."""

    severity: str
    category: str
    description: str
    entity_count: int
    remediation: str


@dataclass(frozen=True)
class PrivacyRecommendation:
    """Immutable representation of a privacy recommendation."""

    priority: str
    description: str
    action: str
    related_entity_types: list[str]


class PrivacyRiskScore(BaseModel):
    """Computes and encapsulates a privacy risk score."""

    model_config = ConfigDict(extra="ignore")

    overall_score: float = 0.0
    entity_scores: list[dict[str, Any]] = Field(default_factory=list)
    sensitivity_breakdown: dict[str, float] = Field(default_factory=dict)
    category_scores: dict[str, float] = Field(default_factory=dict)

    @field_validator("overall_score")
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        """Ensure the overall score is non-negative."""
        if v < 0.0:
            msg: str = "Overall score must be non-negative"
            raise ValueError(msg)
        return v

