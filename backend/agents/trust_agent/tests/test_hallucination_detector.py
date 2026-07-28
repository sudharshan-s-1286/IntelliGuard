import pytest
from agents.trust_agent.detector import HallucinationDetector


@pytest.fixture
def detector() -> HallucinationDetector:
    return HallucinationDetector()


@pytest.mark.asyncio
async def test_clean_prompt_has_no_hallucinations(detector: HallucinationDetector) -> None:
    prompt = "The quick brown fox jumps over the lazy dog on January 15th, 2023."
    result = await detector.analyze(prompt)
    assert result.is_triggered is False
    assert result.score == 100.0
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_impossible_dates(detector: HallucinationDetector) -> None:
    prompt = "It is a known fact that on February 30th, 2025, aliens landed."
    result = await detector.analyze(prompt)
    assert result.is_triggered is True
    assert len(result.findings) == 1
    assert result.findings[0].category == "hallucination.impossible_date"
    
    prompt2 = "We predict that by the year 2199, flying cars will exist."
    result2 = await detector.analyze(prompt2)
    assert result2.is_triggered is True
    assert result2.findings[0].category == "hallucination.impossible_date"


@pytest.mark.asyncio
async def test_fake_citations(detector: HallucinationDetector) -> None:
    prompt = "According to doi: 10.1234/fake-article, this is true."
    result = await detector.analyze(prompt)
    assert result.is_triggered is True
    assert result.findings[0].category == "hallucination.fake_citation"

    prompt2 = "My IP is 300.256.999.0."
    result2 = await detector.analyze(prompt2)
    assert result2.is_triggered is True
    assert result2.findings[0].category == "hallucination.fake_citation"
    
    prompt3 = "Read more at example.com"
    result3 = await detector.analyze(prompt3)
    assert result3.is_triggered is True
    assert result3.findings[0].category == "hallucination.fake_citation"


@pytest.mark.asyncio
async def test_placeholders(detector: HallucinationDetector) -> None:
    prompt = "For more details, see [Insert link here]."
    result = await detector.analyze(prompt)
    assert result.is_triggered is True
    assert result.findings[0].category == "hallucination.placeholder"
    
    prompt2 = "Ref: XXXX-XXXX-XXXX"
    result2 = await detector.analyze(prompt2)
    assert result2.is_triggered is True
    assert result2.findings[0].category == "hallucination.placeholder"


@pytest.mark.asyncio
async def test_unsupported_claims(detector: HallucinationDetector) -> None:
    prompt = "There is absolutely zero evidence that this is false."
    result = await detector.analyze(prompt)
    assert result.is_triggered is True
    assert result.findings[0].category == "hallucination.unsupported_claim"


@pytest.mark.asyncio
async def test_contradictions(detector: HallucinationDetector) -> None:
    prompt = "I cannot answer that. However, here is a detailed 5 paragraph essay on the topic explaining exactly what you asked for in great detail and length so it exceeds 100 characters..."
    result = await detector.analyze(prompt)
    assert result.is_triggered is True
    assert result.findings[0].category == "hallucination.contradiction"
