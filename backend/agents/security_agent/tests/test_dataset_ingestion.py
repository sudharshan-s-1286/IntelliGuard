import pytest

from backend.agents.security_agent.datasets.ingestion.cleaner import DatasetCleaner
from backend.agents.security_agent.datasets.ingestion.normalizers import (
    GarakNormalizer,
    HackAPromptNormalizer,
    OWASPNormalizer,
    ProtectAINormalizer,
)
from backend.agents.security_agent.models.domain import NormalizedDatasetRecord


def test_hackaprompt_normalizer():
    normalizer = HackAPromptNormalizer()
    raw = {"prompt": "test prompt", "expected": "hacked", "level": 4}
    record = normalizer.normalize(raw)
    
    assert record is not None
    assert record.text == "test prompt"
    assert record.severity == "HIGH"
    assert record.source == "hackaprompt"
    assert "level_4" in record.tags
    
    # Missing prompt
    assert normalizer.normalize({"level": 1}) is None


def test_garak_normalizer():
    normalizer = GarakNormalizer()
    raw = {"plugin": "test_plugin", "prompt": "garak test", "goal": "bypass"}
    record = normalizer.normalize(raw)
    
    assert record is not None
    assert record.text == "garak test"
    assert record.subcategory == "test_plugin"
    assert "bypass" in record.tags


def test_owasp_normalizer():
    normalizer = OWASPNormalizer()
    raw = {"text": "owasp test", "category": "Test Cat", "owasp_id": "LLM02"}
    record = normalizer.normalize(raw)
    
    assert record is not None
    assert record.text == "owasp test"
    assert record.category == "Test Cat"
    assert record.owasp == "LLM02"


def test_protect_ai_normalizer():
    normalizer = ProtectAINormalizer()
    raw = {"input": "protect input", "label": "exfiltration"}
    record = normalizer.normalize(raw)
    
    assert record is not None
    assert record.text == "protect input"
    assert record.subcategory == "exfiltration"


def test_dataset_cleaner_whitespace():
    cleaner = DatasetCleaner()
    record = NormalizedDatasetRecord(
        id="test", category="C", subcategory="S", severity="M", owasp="O",
        text="  This   is \n a  test   ", source="src", tags=[]
    )
    
    cleaned = cleaner.clean_record(record)
    assert cleaned is not None
    assert cleaned.text == "This is a test"


def test_dataset_cleaner_duplicates():
    cleaner = DatasetCleaner()
    record1 = NormalizedDatasetRecord(
        id="test1", category="C", subcategory="S", severity="M", owasp="O",
        text="Hello World", source="src", tags=[]
    )
    record2 = NormalizedDatasetRecord(
        id="test2", category="C", subcategory="S", severity="M", owasp="O",
        text="hello world ", source="src", tags=[]
    )
    
    # First should pass
    res1 = cleaner.clean_record(record1)
    assert res1 is not None
    
    # Second should fail as duplicate (after lower/strip)
    res2 = cleaner.clean_record(record2)
    assert res2 is None


def test_dataset_cleaner_batch():
    cleaner = DatasetCleaner()
    records = [
        NormalizedDatasetRecord("1", "C", "S", "M", "O", "test1", "src", []),
        NormalizedDatasetRecord("2", "C", "S", "M", "O", "test2", "src", []),
        NormalizedDatasetRecord("3", "C", "S", "M", "O", " test1 ", "src", []), # duplicate
        NormalizedDatasetRecord("4", "C", "S", "M", "O", "   ", "src", []), # empty
    ]
    
    result = cleaner.clean_batch(records)
    assert result["stats"]["total_input"] == 4
    assert result["stats"]["valid"] == 2
    assert result["stats"]["duplicates_removed"] == 1
    assert result["stats"]["invalid_skipped"] == 1
    assert len(result["cleaned_records"]) == 2
