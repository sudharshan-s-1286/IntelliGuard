import pytest

from backend.agents.security_agent.validators.request_validator import parse_prompt


@pytest.mark.asyncio
async def test_parse_prompt_normal():
    prompt = "  Hello   world!  "
    result = parse_prompt(prompt)
    assert result["original"] == "  Hello   world!  "
    assert result["normalized"] == "Hello world!"
    assert result["was_encoded"] is False

@pytest.mark.asyncio
async def test_parse_prompt_empty():
    result = parse_prompt("")
    assert result["normalized"] == ""

@pytest.mark.asyncio
async def test_parse_prompt_base64():
    # Base64 string > 8 chars to trigger detector
    prompt = "aGVsbG8gd29ybGQ="
    result = parse_prompt(prompt)
    assert result["normalized"] == "hello world"
    assert result["was_encoded"] is True
