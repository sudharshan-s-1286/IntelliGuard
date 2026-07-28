import pytest
from agents.compliance_agent.detector import RegulationChecker


@pytest.fixture
def checker() -> RegulationChecker:
    return RegulationChecker()


def test_detect_gdpr(checker: RegulationChecker) -> None:
    text1 = "Send the report to alice@gmail.com"
    findings1 = checker.detect(text1)
    gdpr1 = [f for f in findings1 if f["regulation"] == "GDPR"]
    assert len(gdpr1) == 1
    assert gdpr1[0]["description"] == "Personal email disclosed."
    assert gdpr1[0]["severity"] == "High"

    text2 = "We shared user profiles without consent."
    findings2 = checker.detect(text2)
    gdpr2 = [f for f in findings2 if f["regulation"] == "GDPR"]
    assert len(gdpr2) == 1
    assert gdpr2[0]["description"] == "Missing user consent."

    text3 = "This dump user db includes everything."
    findings3 = checker.detect(text3)
    gdpr3 = [f for f in findings3 if f["regulation"] == "GDPR"]
    assert len(gdpr3) == 1
    assert gdpr3[0]["description"] == "Excessive disclosure of personal details."


def test_detect_hipaa(checker: RegulationChecker) -> None:
    text = "Patient ID 555-123 is diagnosed with cancer and needs prescription: chemotherapy."
    findings = checker.detect(text)
    hipaa = [f for f in findings if f["regulation"] == "HIPAA"]
    
    assert len(hipaa) >= 3
    descriptions = [h["description"] for h in hipaa]
    assert "Exposed patient identifier." in descriptions
    assert "Exposed medical diagnosis details." in descriptions
    assert "Exposed treatment or therapy records." in descriptions


def test_detect_pci(checker: RegulationChecker) -> None:
    text = "Exposed card number: 4111 1111 1111 1111 with cvv 123."
    findings = checker.detect(text)
    pci = [f for f in findings if f["regulation"] == "PCI-DSS"]
    
    assert len(pci) == 2
    descriptions = [p["description"] for p in pci]
    assert "Exposed payment card numbers." in descriptions
    assert "Exposed card authentication data." in descriptions


def test_detect_soc2(checker: RegulationChecker) -> None:
    text = "Config has api_key: 'myapikey123' and bearer abc123jwt"
    findings = checker.detect(text)
    soc2 = [f for f in findings if f["regulation"] == "SOC2"]
    
    assert len(soc2) == 2
    descriptions = [s["description"] for s in soc2]
    assert "Exposed system credentials." in descriptions
    assert "Exposed auth tokens or session data." in descriptions


def test_detect_iso27001(checker: RegulationChecker) -> None:
    text = "We will disable firewall to run this test."
    findings = checker.detect(text)
    iso = [f for f in findings if f["regulation"] == "ISO27001"]
    
    assert len(iso) == 1
    assert iso[0]["description"] == "Security policy compliance violation."
    assert iso[0]["severity"] == "High"


def test_overlap_deduplication(checker: RegulationChecker) -> None:
    # A card verification pin "pin number" should not overlap with nested parts
    text = "Please enter your pin number"
    findings = checker.detect(text)
    pci = [f for f in findings if f["regulation"] == "PCI-DSS"]
    assert len(pci) == 1
    assert pci[0]["description"] == "Exposed card authentication data."


def test_no_violations(checker: RegulationChecker) -> None:
    text = "Standard greeting message. No issues."
    findings = checker.detect(text)
    assert len(findings) == 0


def test_empty_string(checker: RegulationChecker) -> None:
    findings = checker.detect("")
    assert len(findings) == 0
