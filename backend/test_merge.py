from agents.security_agent.models.domain import Finding, Threat
from agents.security_agent.detectors.decision_engine import DecisionEngine

de = DecisionEngine(None)
f = Finding(
    threat=Threat(category="Prompt Injection", description="Test"),
    severity=0.9,
    evidence="Test",
    detector="SemanticDetector",
    confidence=0.9,
    metadata={"similarity_score": 0.9}
)

explainability = []
recommendations = []
merged = de._resolve_duplicates([f], explainability, recommendations)
print("Merged:", len(merged))
