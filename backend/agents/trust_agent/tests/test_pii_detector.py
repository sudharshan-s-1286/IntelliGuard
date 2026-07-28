import pytest
from fastapi import status
from httpx import AsyncClient

from agents.trust_agent.detector import PIIDetector, PIIEntityType


@pytest.mark.asyncio
async def test_valid_email_detection() -> None:
    """Tests detection of valid email address PII entity."""
    detector = PIIDetector()
    prompt = "Please contact me at john.doe@example.com for further details."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    assert result.score < 90.0
    assert len(result.findings) >= 1
    
    email_findings = [f for f in result.findings if f.category == "pii.email"]
    assert len(email_findings) == 1
    assert email_findings[0].metadata["matched_value"] == "john.doe@example.com"
    assert email_findings[0].metadata["masked_value"] == "j***@example.com"


@pytest.mark.asyncio
async def test_invalid_email_rejection() -> None:
    """Tests that malformed email strings are not detected as valid emails."""
    detector = PIIDetector()
    prompt = "This is not an email: john.doe@ or @example.com or user@.com."
    result = await detector.analyze(prompt)

    email_findings = [f for f in result.findings if f.category == "pii.email"]
    assert len(email_findings) == 0


@pytest.mark.asyncio
async def test_phone_number_detection() -> None:
    """Tests detection of US/International phone numbers."""
    detector = PIIDetector()
    prompt = "Call our support hotline at 9876543210 or +1-555-123-4567 immediately."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    phone_findings = [f for f in result.findings if f.category == "pii.phone_number"]
    assert len(phone_findings) >= 1


@pytest.mark.asyncio
async def test_credit_card_detection_with_luhn() -> None:
    """Tests credit card detection with Luhn algorithm validation (valid vs invalid checksum)."""
    detector = PIIDetector()
    
    # Valid Visa card passing Luhn check: 4532015112830366
    valid_card_prompt = "Payment card number: 4532015112830366"
    valid_result = await detector.analyze(valid_card_prompt)

    assert valid_result.is_triggered is True
    card_findings = [f for f in valid_result.findings if f.category == "pii.credit_card"]
    assert len(card_findings) == 1
    assert card_findings[0].metadata["masked_value"].startswith("4532")

    # Invalid card number failing Luhn check: 4532015112830367
    invalid_card_prompt = "Invalid card sequence: 4532015112830367"
    invalid_result = await detector.analyze(invalid_card_prompt)
    invalid_card_findings = [f for f in invalid_result.findings if f.category == "pii.credit_card"]
    assert len(invalid_card_findings) == 0


@pytest.mark.asyncio
async def test_aws_access_key_detection() -> None:
    """Tests detection of AWS Access Key IDs."""
    detector = PIIDetector()
    prompt = "Configure environment with AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    aws_findings = [f for f in result.findings if f.category == "pii.aws_access_key"]
    assert len(aws_findings) == 1
    assert aws_findings[0].metadata["matched_value"] == "AKIAIOSFODNN7EXAMPLE"
    assert "AKI-************" in aws_findings[0].metadata["masked_value"]


@pytest.mark.asyncio
async def test_openai_api_key_detection() -> None:
    """Tests detection of OpenAI secret API keys."""
    detector = PIIDetector()
    prompt = "Use API key: sk-proj-1234567890abcdef1234567890abcdef"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    openai_findings = [f for f in result.findings if f.category == "pii.openai_api_key"]
    assert len(openai_findings) == 1
    assert openai_findings[0].metadata["matched_value"] == "sk-proj-1234567890abcdef1234567890abcdef"


@pytest.mark.asyncio
async def test_jwt_detection() -> None:
    """Tests detection of JSON Web Tokens (JWT)."""
    detector = PIIDetector()
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    prompt = f"Bearer {jwt_token}"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    jwt_findings = [f for f in result.findings if f.category == "pii.jwt_token"]
    assert len(jwt_findings) >= 1


@pytest.mark.asyncio
async def test_aadhaar_detection() -> None:
    """Tests detection of India Aadhaar identity numbers."""
    detector = PIIDetector()
    prompt = "Aadhaar number for identity verification: 3675 9834 6210"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    aadhaar_findings = [f for f in result.findings if f.category == "pii.in_aadhaar"]
    assert len(aadhaar_findings) == 1
    assert aadhaar_findings[0].metadata["masked_value"] == "**** **** 6210"


@pytest.mark.asyncio
async def test_pan_detection() -> None:
    """Tests detection of India Permanent Account Number (PAN)."""
    detector = PIIDetector()
    prompt = "Taxpayer PAN details: ABCDE1234F"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    pan_findings = [f for f in result.findings if f.category == "pii.in_pan"]
    assert len(pan_findings) == 1
    assert pan_findings[0].metadata["matched_value"] == "ABCDE1234F"
    assert pan_findings[0].metadata["masked_value"] == "AB*****4F"


@pytest.mark.asyncio
async def test_passport_detection() -> None:
    """Tests detection of passport identity numbers."""
    detector = PIIDetector()
    prompt = "Travel document passport number: A1234567"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    passport_findings = [f for f in result.findings if f.category == "pii.passport_number"]
    assert len(passport_findings) == 1


@pytest.mark.asyncio
async def test_ipv4_detection() -> None:
    """Tests detection of IPv4 address strings."""
    detector = PIIDetector()
    prompt = "Connecting to database server at 192.168.1.100"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    ipv4_findings = [f for f in result.findings if f.category == "pii.ipv4_address"]
    assert len(ipv4_findings) == 1
    assert ipv4_findings[0].metadata["masked_value"] == "192.168.*.*"


@pytest.mark.asyncio
async def test_ipv6_detection() -> None:
    """Tests detection of IPv6 address strings."""
    detector = PIIDetector()
    prompt = "IPv6 endpoint address: 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    ipv6_findings = [f for f in result.findings if f.category == "pii.ipv6_address"]
    assert len(ipv6_findings) == 1


@pytest.mark.asyncio
async def test_multiple_entities_in_one_prompt() -> None:
    """Tests detection of multiple distinct PII entity types in a single prompt payload."""
    detector = PIIDetector()
    prompt = (
        "User user@example.com with phone 9876543210 and AWS Key AKIAIOSFODNN7EXAMPLE "
        "requested access from IP 10.0.0.1"
    )
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    assert result.score < 50.0
    assert len(result.findings) >= 4
    categories = {f.category for f in result.findings}
    assert "pii.email" in categories
    assert "pii.phone_number" in categories
    assert "pii.aws_access_key" in categories
    assert "pii.ipv4_address" in categories


@pytest.mark.asyncio
async def test_false_positive_prevention() -> None:
    """Tests benign prompts to ensure zero false positive PII triggers and 100.0 score."""
    detector = PIIDetector()
    prompt = "What is the capital of France? Explain quantum physics in simple terms."
    result = await detector.analyze(prompt)

    assert result.is_triggered is False
    assert result.score == 100.0
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_empty_prompt() -> None:
    """Tests handling of empty or whitespace-only prompts."""
    detector = PIIDetector()
    for empty_text in ["", "    ", "\n\t"]:
        result = await detector.analyze(empty_text)
        assert result.is_triggered is False
        assert result.score == 100.0
        assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_masked_output_validation() -> None:
    """Validates that all findings contain proper masked representations protecting sensitive values."""
    detector = PIIDetector()
    prompt = "Email: alice@company.org, PAN: WXYZP9876Q"
    result = await detector.analyze(prompt)

    for finding in result.findings:
        assert "masked_value" in finding.metadata
        assert "matched_value" in finding.metadata
        # Masked value should differ from raw matched sensitive value
        assert finding.metadata["masked_value"] != finding.metadata["matched_value"]


@pytest.mark.asyncio
async def test_api_trust_analyze_endpoint_with_pii(
    async_client: AsyncClient,
) -> None:
    """Integration test: verifies POST /api/v1/trust/analyze returns PIIDetector findings."""
    payload = {
        "prompt": "Please email sensitive report to secret.user@corp.com with AWS Key AKIAIOSFODNN7EXAMPLE"
    }
    response = await async_client.post("/api/v1/trust/analyze", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["success"] is True
    assert data["data"]["overall_status"] in ("MEDIUM_RISK", "HIGH_RISK", "CRITICAL_RISK")
    assert data["data"]["trust_score"] < 60.0
    
    detector_names = [f["detector_name"] for f in data["data"]["findings"]]
    assert "pii_detector" in detector_names
    
    pii_findings = [f for f in data["data"]["findings"] if f["detector_name"] == "pii_detector"]
    assert len(pii_findings) >= 2
