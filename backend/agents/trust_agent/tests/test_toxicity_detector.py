import pytest
from fastapi import status
from httpx import AsyncClient

from agents.trust_agent.detector import ToxicityCategory, ToxicityDetector


@pytest.mark.asyncio
async def test_profanity_detection() -> None:
    """Tests detection of vulgar profanity."""
    detector = ToxicityDetector()
    prompt = "This is total bullshit and a complete waste of time."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    assert len(result.findings) >= 1
    categories = {f.category for f in result.findings}
    assert "toxicity.profanity" in categories


@pytest.mark.asyncio
async def test_insult_detection() -> None:
    """Tests detection of personal insults and derogatory name-calling."""
    detector = ToxicityDetector()
    prompt = "You are an absolute idiot and a complete moron."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    categories = {f.category for f in result.findings}
    assert "toxicity.insult" in categories


@pytest.mark.asyncio
async def test_harassment_detection() -> None:
    """Tests detection of targeted harassment and intimidation."""
    detector = ToxicityDetector()
    prompt = "Nobody likes you here, you should die."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    categories = {f.category for f in result.findings}
    assert "toxicity.harassment" in categories


@pytest.mark.asyncio
async def test_hate_speech_detection() -> None:
    """Tests detection of hate speech slurs and group attacks."""
    detector = ToxicityDetector()
    prompt = "I hate all foreigners and they should be expelled."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    categories = {f.category for f in result.findings}
    assert "toxicity.hate_speech" in categories


@pytest.mark.asyncio
async def test_threat_detection() -> None:
    """Tests detection of explicit physical violence threats."""
    detector = ToxicityDetector()
    prompt = "I will kill you if I ever see you again."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    assert result.score <= 50.0
    categories = {f.category for f in result.findings}
    assert "toxicity.threat" in categories


@pytest.mark.asyncio
async def test_violence_detection() -> None:
    """Tests detection of graphic descriptions of violence."""
    detector = ToxicityDetector()
    prompt = "The scene described a brutal massacre and decapitation."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    categories = {f.category for f in result.findings}
    assert "toxicity.violence" in categories


@pytest.mark.asyncio
async def test_sexual_content_detection() -> None:
    """Tests detection of non-consensual or explicit sexual content."""
    detector = ToxicityDetector()
    prompt = "Requesting explicit pornography content payload."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    categories = {f.category for f in result.findings}
    assert "toxicity.sexual_content" in categories


@pytest.mark.asyncio
async def test_self_harm_detection() -> None:
    """Tests detection of self-harm or suicide statements."""
    detector = ToxicityDetector()
    prompt = "I want to kill myself right now."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    assert result.score <= 50.0
    categories = {f.category for f in result.findings}
    assert "toxicity.self_harm" in categories


@pytest.mark.asyncio
async def test_discrimination_detection() -> None:
    """Tests detection of discriminatory or bigoted statements."""
    detector = ToxicityDetector()
    prompt = "They are an inferior race and we must discriminate against them."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    categories = {f.category for f in result.findings}
    assert "toxicity.discrimination" in categories


@pytest.mark.asyncio
async def test_cyberbullying_detection() -> None:
    """Tests detection of cyberbullying and doxxing campaigns."""
    detector = ToxicityDetector()
    prompt = "Let's doxx this person and expose their address immediately."
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    categories = {f.category for f in result.findings}
    assert "toxicity.cyberbullying" in categories


@pytest.mark.asyncio
async def test_leetspeak_deobfuscation() -> None:
    """Tests de-obfuscation of leetspeak evasion attempts (e.g. k!ll y0ur$3lf)."""
    detector = ToxicityDetector()
    prompt = "go k!ll y0ur$3lf right now"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    categories = {f.category for f in result.findings}
    assert "toxicity.self_harm" in categories


@pytest.mark.asyncio
async def test_all_caps_aggression_heuristics() -> None:
    """Tests heuristic detection of aggressive ALL-CAPS shouting."""
    detector = ToxicityDetector()
    prompt = "STOP THIS IMMEDIATELY YOU TERRIBLE PERSON!!!"
    result = await detector.analyze(prompt)

    assert result.is_triggered is True
    assert len(result.findings) >= 1


@pytest.mark.asyncio
async def test_benign_prompt_false_positives() -> None:
    """Tests benign prompts returning clean SAFE status and 100.0 score."""
    detector = ToxicityDetector()
    prompt = "The weather today is warm and sunny with a gentle breeze."
    result = await detector.analyze(prompt)

    assert result.is_triggered is False
    assert result.score == 100.0
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_empty_prompt_handling() -> None:
    """Tests handling of empty or whitespace inputs."""
    detector = ToxicityDetector()
    for empty_input in ["", "   ", "\t\n"]:
        result = await detector.analyze(empty_input)
        assert result.is_triggered is False
        assert result.score == 100.0
        assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_api_trust_analyze_endpoint_with_toxicity(
    async_client: AsyncClient,
) -> None:
    """Integration test: verifies POST /api/v1/trust/analyze returns ToxicityDetector findings."""
    payload = {"prompt": "I will kill you and doxx your home address"}
    response = await async_client.post("/api/v1/trust/analyze", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["success"] is True
    assert data["data"]["overall_status"] in ("MEDIUM_RISK", "HIGH_RISK", "CRITICAL_RISK")
    assert data["data"]["trust_score"] < 60.0

    detector_names = [f["detector_name"] for f in data["data"]["findings"]]
    assert "toxicity_detector" in detector_names
