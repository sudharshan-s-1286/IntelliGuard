import pytest
from agents.compliance_agent.detector import ToxicityDetector


@pytest.fixture
def detector() -> ToxicityDetector:
    return ToxicityDetector()


def test_detect_hate_speech(detector: ToxicityDetector) -> None:
    text = "Do not spread hate or incite_hatred in this forum."
    findings = detector.detect(text)
    
    violations = [f for f in findings if f["category"] == "Hate Speech"]
    assert len(violations) == 1
    assert violations[0]["matched"] == "incite_hatred"
    assert violations[0]["severity"] == "High"


def test_detect_harassment(detector: ToxicityDetector) -> None:
    text = "We should not harass or stalk anyone."
    findings = detector.detect(text)
    
    violations = [f for f in findings if f["category"] == "Harassment"]
    assert len(violations) == 1
    assert violations[0]["matched"] == "stalk"
    assert violations[0]["severity"] == "Medium"


def test_detect_violence(detector: ToxicityDetector) -> None:
    text = "The attacker tried to murder the bystander."
    findings = detector.detect(text)
    
    violations = [f for f in findings if f["category"] == "Violence"]
    assert len(violations) == 1
    assert violations[0]["matched"] == "murder"
    assert violations[0]["severity"] == "High"


def test_detect_threats(detector: ToxicityDetector) -> None:
    text = "A bomb threat was reported at the venue."
    findings = detector.detect(text)
    
    violations = [f for f in findings if f["category"] == "Threats"]
    assert len(violations) == 1
    assert violations[0]["matched"] == "bomb"
    assert violations[0]["severity"] == "High"


def test_detect_offensive_language(detector: ToxicityDetector) -> None:
    text = "Stop calling him a bastard, it is offensive."
    findings = detector.detect(text)
    
    violations = [f for f in findings if f["category"] == "Offensive Language"]
    assert len(violations) == 1
    assert violations[0]["matched"] == "bastard"
    assert violations[0]["severity"] == "Medium"


def test_detect_discrimination(detector: ToxicityDetector) -> None:
    text = "The comment made was racist and inappropriate."
    findings = detector.detect(text)
    
    violations = [f for f in findings if f["category"] == "Discrimination"]
    assert len(violations) == 1
    assert violations[0]["matched"] == "racist"
    assert violations[0]["severity"] == "High"


def test_overlap_deduplication(detector: ToxicityDetector) -> None:
    # Set up overlapping text like "beatup" which is matching violence.
    # If there is a rule pattern that matches "up" and "beatup", "beatup" should win.
    text = "They plan to beatup the target."
    findings = detector.detect(text)
    
    violations = [f for f in findings if f["category"] == "Violence"]
    assert len(violations) == 1
    assert violations[0]["matched"] == "beatup"


def test_no_toxicity(detector: ToxicityDetector) -> None:
    text = "Welcome to our safe and clean community chat room."
    findings = detector.detect(text)
    assert len(findings) == 0


def test_empty_string(detector: ToxicityDetector) -> None:
    findings = detector.detect("")
    assert len(findings) == 0
