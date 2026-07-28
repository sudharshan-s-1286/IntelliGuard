# Privacy Agent

Production-grade Privacy Agent for the IntelliGuard AI security platform.

## Overview

The Privacy Agent is responsible exclusively for privacy-related analysis:
- **Detecting** Personally Identifiable Information (PII) in text
- **Classifying** detected entities by category
- **Masking** sensitive information
- **Calculating** a Privacy Risk Score
- **Generating** structured findings and recommendations

## Architecture

This project follows Clean Architecture and SOLID principles:

```
privacy_agent/
+-- agent.py              # Main PrivacyAgent entry point
+-- detector.py           # PII detection engine
+-- classifier.py         # Entity classification engine
+-- masker.py             # Information masking engine
+-- scoring.py            # Privacy risk scoring engine
+-- validator.py          # Input/output validation
+-- schemas.py            # Pydantic v2 request/response schemas
+-- models.py             # Domain models (PIIEntity, findings, etc.)
+-- config.py             # Configuration management
+-- utils.py              # Utility functions
+-- exceptions.py         # Custom exception hierarchy
+-- logging_config.py     # Structured logging configuration
+-- constants.py          # PII types, patterns, and thresholds
+-- tests/                # Test suite
+-- README.md             # This file
```

## Installation

```bash
# No external dependencies beyond Python 3.12+ and Pydantic v2
pip install pydantic>=2.0
```

## Dependencies

- Python 3.12+
- Pydantic v2
- Standard library: `re`, `dataclasses`, `logging`, `hashlib`, `uuid`, `enum`

## Configuration

```python
from privacy_agent import PrivacyAgent, PrivacyAgentConfig

config = PrivacyAgentConfig(
    confidence_threshold=0.7,
    risk_score_cap=100.0,
    enable_masking=True,
    enable_classification=True,
    enable_scoring=True,
    log_level="INFO",
)
agent = PrivacyAgent(config=config)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `confidence_threshold` | `float` | `0.5` | Minimum confidence for PII detection (0.0–1.0) |
| `max_entities_per_scan` | `int` | `1000` | Maximum entities to detect per scan |
| `risk_score_cap` | `float` | `100.0` | Upper bound for computed risk score |
| `enable_masking` | `bool` | `True` | Whether to perform information masking |
| `enable_classification` | `bool` | `True` | Whether to classify detected entities |
| `enable_scoring` | `bool` | `True` | Whether to compute a privacy risk score |
| `log_level` | `str` | `"INFO"` | Logging verbosity level |

## Supported PII Entities

The Privacy Agent detects the following entity types via regex patterns:

- **Email addresses** — RFC-style email patterns
- **Phone numbers** — US phone numbers (10–11 digits)
- **Social Security Numbers (SSN)** — `DDD-DD-DDDD` format
- **Credit card numbers** — 16-digit formats with Luhn validation
- **IP addresses** — IPv4 dotted-quad notation
- **Dates of birth** — `MM/DD/YYYY` format
- **Medical records** — `Medical Record #` prefixed identifiers

## Risk Scoring Methodology

The privacy risk score is computed as a weighted sum of per-entity contributions:

```
entity_score = confidence × sensitivity_weight × 10.0
overall_score = min(sum(entity_scores), risk_score_cap)
```

**Sensitivity weights:**
- `high` — 1.0 (SSN, credit card, passport, driver license, medical record, financial account)
- `medium` — 0.6 (email, phone, IP address)
- `low` — 0.2 (name, address, date of birth)

**Risk levels:**
- `low` — 0.0 – 24.9
- `medium` — 25.0 – 49.9
- `high` — 50.0 – 74.9
- `critical` — 75.0 – 100.0

## Masking Strategy

The agent supports two masking strategies via the Strategy pattern:

- **RedactionMasker** — Replaces the entire value with a placeholder (default: `***`)
- **PartialMasker** — Preserves prefix and suffix characters, masks the middle

## Input Schema

The Privacy Agent follows the IntelliGuard Orchestrator Agent contract:

```json
{
    "request_id": "uuid",
    "text": "string containing potential PII",
    "metadata": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | `string` | No | Unique request identifier |
| `text` | `string` | Yes | Text to scan for PII |
| `metadata` | `dict` | No | Contextual metadata passed through |

## Output Schema

```json
{
    "status": "success",
    "agent": "PrivacyAgent",
    "request_id": "uuid",
    "risk_score": 0.0,
    "risk_level": "low",
    "findings": [],
    "recommendations": [],
    "metadata": {},
    "errors": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | `string` | `"success"` or `"error"` |
| `agent` | `string` | Always `"PrivacyAgent"` |
| `request_id` | `string` | Passed through from input |
| `risk_score` | `float` | Overall privacy risk score (0.0–100.0) |
| `risk_level` | `string` | `"low"`, `"medium"`, `"high"`, or `"critical"` |
| `findings` | `list[dict]` | Structured privacy findings |
| `recommendations` | `list[str]` | Actionable recommendations |
| `metadata` | `dict` | Passed through from input |
| `errors` | `list[str]` | Error messages, empty on success |

## Example Usage

### Basic Usage

```python
from privacy_agent import PrivacyAgent

agent = PrivacyAgent()
response = agent.run({
    "request_id": "req-123",
    "text": "Contact alice@example.com or call 555-123-4567",
})

print(response["status"])        # "success"
print(response["risk_score"])    # 10.8
print(response["risk_level"])    # "low"
print(response["findings"])      # [{"severity": "low", ...}]
```

### Integration with Orchestrator Agent

```python
from privacy_agent import PrivacyAgent

class OrchestratorAgent:
    def __init__(self) -> None:
        self._privacy_agent = PrivacyAgent()

    def process(self, request: dict) -> dict:
        privacy_response = self._privacy_agent.run(request)
        return {
            "orchestrator_status": "complete",
            "privacy": privacy_response,
            "trust": self._trust_agent.process(privacy_response),
        }
```

### Error Handling

```python
response = agent.run({
    "request_id": "req-err",
    "text": "",
})

assert response["status"] == "error"
assert len(response["errors"]) > 0
assert response["risk_score"] == 0.0
```

## Testing

Run the test suite with:

```bash
pytest tests/ -v
```

- **Unit tests** (`tests/unit/`) — 61 tests covering individual modules
- **Integration tests** (`tests/integration/`) — 18 tests covering Orchestrator contract, edge cases, and JSON serialization

## Extension Guide

To add a new PII entity type:

1. Add the type constant in `constants.py`
2. Add the regex pattern in `detector.py` (`PII_PATTERNS`)
3. Add sensitivity mapping in `constants.py` (`PII_SENSITIVITY`)
4. Add classification rule in `classifier.py` (`CLASSIFICATION_RULES`)
5. Add tests in `tests/unit/test_detector.py`

To add a new masking strategy:

1. Implement `MaskingStrategy` interface in `masker.py`
2. Inject via `PrivacyMasker(config, strategy=NewStrategy())`

## License

Internal use — IntelliGuard Platform
