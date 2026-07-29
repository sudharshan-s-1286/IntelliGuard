"""Domain Models for Security Agent."""
from dataclasses import dataclass
from typing import Any


@dataclass
class Threat:
    """Categorizes the type of attack."""
    category: str
    description: str

@dataclass
class Finding:
    """Represents a specific matched rule or semantic hit."""
    threat: Threat
    severity: float
    evidence: str
    detector: str = "Unknown"
    confidence: float = 0.0

@dataclass
class RiskScore:
    """Encapsulates the final computed risk."""
    score: float
    factors: list[str]

@dataclass
class Recommendation:
    """Actionable advice based on findings."""
    action: str
    priority: str

@dataclass
class PatternMatch:
    """Result from a vector DB search."""
    pattern_id: str
    similarity_score: float
    metadata: dict[str, Any]

@dataclass
class Metadata:
    """Execution metadata."""
    execution_time_ms: float
    model_versions: dict[str, str]

@dataclass
class RoutingDecision:
    """Indicates if an LLM is required and why."""
    needs_llm: bool
    reason: str

@dataclass
class LLMClassificationResponse:
    """Structured output expected from the LLM."""
    attack_category: str
    confidence: float
    reasoning: str
    evidence: str
    recommendations: list[str]
    uncertainty: str

@dataclass
class DetectionResult:
    """The internal aggregation of all findings."""
    risk_score: RiskScore
    findings: list[Finding]
    recommendations: list[Recommendation]
    metadata: Metadata
    routing: RoutingDecision = None
    explainability: list[str] = None

    def __post_init__(self):
        if self.routing is None:
            self.routing = RoutingDecision(needs_llm=False, reason="Default initialization")
        if self.explainability is None:
            self.explainability = []

@dataclass
class VectorMetadata:
    """Metadata schema for stored vectors in Qdrant."""
    pattern_id: str
    category: str
    attack_type: str
    severity: str
    owasp_mapping: str
    description: str
    source: str
    dataset_version: str
    created_at: str
    updated_at: str
    tags: list[str]
