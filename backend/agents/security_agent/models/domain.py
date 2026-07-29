"""Domain Models for Security Agent."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

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
    factors: List[str]

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
    metadata: Dict[str, Any]

@dataclass
class Metadata:
    """Execution metadata."""
    execution_time_ms: float
    model_versions: Dict[str, str]

@dataclass
class RoutingDecision:
    """Indicates if an LLM is required and why."""
    needs_llm: bool
    reason: str

@dataclass
class DetectionResult:
    """The internal aggregation of all findings."""
    risk_score: RiskScore
    findings: List[Finding]
    recommendations: List[Recommendation]
    metadata: Metadata
    routing: RoutingDecision = None
    explainability: List[str] = None

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
    tags: List[str]
