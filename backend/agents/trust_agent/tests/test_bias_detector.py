import pytest
from agents.trust_agent.detector import BiasDetector


@pytest.fixture
def detector() -> BiasDetector:
    return BiasDetector()


@pytest.mark.asyncio
async def test_clean_inclusive_prompt(detector: BiasDetector) -> None:
    prompt = "We welcome all men and women to apply for this engineering role."
    result = await detector.analyze(prompt)
    assert result.is_triggered is False
    assert result.score == 100.0
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_occupational_exclusion_gender(detector: BiasDetector) -> None:
    prompt = "Women cannot be a good firefighter."
    result = await detector.analyze(prompt)
    assert result.is_triggered is True
    assert any(f.category == "bias.gender" for f in result.findings)
    assert any("Occupational stereotype" in f.description for f in result.findings)


@pytest.mark.asyncio
async def test_negative_traits_race(detector: BiasDetector) -> None:
    prompt = "It is a known fact that certain white people are inherently greedy."
    result = await detector.analyze(prompt)
    assert result.is_triggered is True
    assert any(f.category == "bias.race_ethnicity" for f in result.findings)
    assert any("Derogatory or stereotyping trait" in f.description for f in result.findings)


@pytest.mark.asyncio
async def test_academic_context_false_positive_reduction(detector: BiasDetector) -> None:
    prompt = "A recent demographics study analyzed why some communities believe that immigrants are dangerous, highlighting systemic issues."
    result = await detector.analyze(prompt)
    # The term 'study' and 'demographics' should suppress the negative trait matching
    assert result.is_triggered is False
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_multiple_biases_deduplication(detector: BiasDetector) -> None:
    prompt = "Those disabled people are lazy. Yes, very lazy disabled individuals."
    result = await detector.analyze(prompt)
    assert result.is_triggered is True
    
    disabled_findings = [f for f in result.findings if f.category == "bias.disability"]
    # We should only have 1 finding for "Derogatory or stereotyping trait" despite it matching twice
    assert len(disabled_findings) == 1
