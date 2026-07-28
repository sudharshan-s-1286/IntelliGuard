import pytest
from agents.compliance_agent.detector import PIIDetector


@pytest.fixture
def detector() -> PIIDetector:
    return PIIDetector()


def test_detect_email(detector: PIIDetector) -> None:
    text = "Send your queries to support@company.com or contact admin@example.org."
    findings = detector.detect(text)
    
    emails = [f for f in findings if f["type"] == "EMAIL"]
    assert len(emails) == 2
    assert any(e["text"] == "support@company.com" for e in emails)
    assert any(e["text"] == "admin@example.org" for e in emails)
    assert all(e["severity"] == "HIGH" for e in emails)


def test_detect_phone(detector: PIIDetector) -> None:
    text = "Call me at +1 (555) 019-2834 or directly at 555-123-4567."
    findings = detector.detect(text)
    
    phones = [f for f in findings if f["type"] == "PHONE"]
    assert len(phones) == 2
    assert any("555" in p["text"] for p in phones)
    assert all(p["severity"] == "MEDIUM" for p in phones)


def test_detect_aadhaar(detector: PIIDetector) -> None:
    text = "My Aadhaar details: 9000 1234 5678 and another one is 912345678901."
    findings = detector.detect(text)
    
    aadhaar = [f for f in findings if f["type"] == "AADHAAR"]
    assert len(aadhaar) == 2
    assert any(a["text"] == "9000 1234 5678" for a in aadhaar)
    assert any(a["text"] == "912345678901" for a in aadhaar)


def test_detect_ssn(detector: PIIDetector) -> None:
    text = "The SSN is 666-29-9234."
    findings = detector.detect(text)
    
    ssns = [f for f in findings if f["type"] == "SSN"]
    assert len(ssns) == 1
    assert ssns[0]["text"] == "666-29-9234"


def test_detect_passport(detector: PIIDetector) -> None:
    text = "Passport number is Z1234567 (IN) or 123456789 (US)."
    findings = detector.detect(text)
    
    passports = [f for f in findings if f["type"] == "PASSPORT"]
    assert len(passports) == 2
    assert any(p["text"] == "Z1234567" for p in passports)
    assert any(p["text"] == "123456789" for p in passports)


def test_detect_credit_card(detector: PIIDetector) -> None:
    text = "Visa card: 4111 1111 1111 1111, Amex: 3782-822463-10005."
    findings = detector.detect(text)
    
    cards = [f for f in findings if f["type"] == "CREDIT_CARD"]
    assert len(cards) == 2
    assert any(c["text"] == "4111 1111 1111 1111" for c in cards)
    assert any(c["text"] == "3782-822463-10005" for c in cards)


def test_detect_bank_account(detector: PIIDetector) -> None:
    text = "Direct deposit details: Account Number 123456789012."
    findings = detector.detect(text)
    
    accounts = [f for f in findings if f["type"] == "BANK_ACCOUNT"]
    assert len(accounts) == 1
    assert accounts[0]["text"] == "123456789012"


def test_overlap_deduplication(detector: PIIDetector) -> None:
    # A 16-digit credit card number should not be matched as a bank account number
    # because they cover the exact same text span, and credit card takes precedence.
    text = "My card is 4111111111111111"
    findings = detector.detect(text)
    
    # Check that we only detect a CREDIT_CARD and no overlapping BANK_ACCOUNT
    assert len(findings) == 1
    assert findings[0]["type"] == "CREDIT_CARD"
    assert findings[0]["text"] == "4111111111111111"


def test_custom_patterns() -> None:
    # Test adding a custom pattern or overriding
    custom = {
        "IP_ADDRESS": {
            "pattern": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            "severity": "MEDIUM"
        },
        "EMAIL": {
            "pattern": r"\b[a-z]+@internal\.corp\b",
            "severity": "CRITICAL"
        }
    }
    custom_detector = PIIDetector(custom_patterns=custom)
    
    text = "Contact me at user@internal.corp or check host 192.168.1.1. Also normal mail user@gmail.com"
    findings = custom_detector.detect(text)
    
    ips = [f for f in findings if f["type"] == "IP_ADDRESS"]
    emails = [f for f in findings if f["type"] == "EMAIL"]
    
    assert len(ips) == 1
    assert ips[0]["text"] == "192.168.1.1"
    
    # Custom email pattern should match user@internal.corp (severity critical)
    # but since we overrode standard email pattern with a specific custom pattern,
    # standard user@gmail.com might no longer match or match differently.
    assert len(emails) == 1
    assert emails[0]["text"] == "user@internal.corp"
    assert emails[0]["severity"] == "CRITICAL"


def test_no_pii(detector: PIIDetector) -> None:
    text = "This is a simple text document without any PII."
    findings = detector.detect(text)
    assert len(findings) == 0


def test_empty_string(detector: PIIDetector) -> None:
    findings = detector.detect("")
    assert len(findings) == 0
