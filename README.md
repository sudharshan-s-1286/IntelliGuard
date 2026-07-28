# Trust-Agent Backend Foundation & Orchestrator

Production-ready, highly scalable Python FastAPI backend scaffold for **Trust-Agent**, part of the **IntelliGuard** platform.

This project implements Clean Architecture and SOLID principles to provide a robust infrastructure foundation and orchestration layer. It is designed to seamlessly integrate future trust, security, compliance, and evaluation engine modules without altering the core system architecture.

---

## Table of Contents

- [Architectural Highlights](#architectural-highlights)
- [Project Directory Structure](#project-directory-structure)
- [Technology Stack](#technology-stack)
- [Prerequisites & Installation](#prerequisites--installation)
- [Running the Server](#running-the-server)
- [Testing](#testing)
- [API Specification](#api-specification)
- [Orchestration Architecture](#orchestration-architecture)
- [Future Extension Strategy](#future-extension-strategy)

---

## Architectural Highlights

- **Clean Architecture & SOLID**: Strict separation between API presentation layer (`app/api`), orchestration layer (`app/agents`), pipeline execution (`AnalysisPipeline`), abstract detector interfaces (`app/detectors`), infrastructure (`app/core`), and schemas (`app/schemas`).
- **Orchestration & Analysis Pipeline**: Dedicated `TrustAgent` and `AnalysisPipeline` layer separating workflow coordination from detector execution.
- **Future Parallel Execution Ready**: Sequential detector execution model designed to support transparent `asyncio.gather` concurrency upgrades with zero detector interface changes.
- **Structured JSON Logging**: Production-ready structured logging with contextual request correlation IDs (`X-Request-ID`).
- **Pydantic v2 Settings**: Strongly typed environment configuration management powered by `pydantic-settings`.
- **Global Exception Mapping**: Unified error response envelope (`APIResponse[T]`) mapping custom domain exceptions, validation errors, and unhandled panics cleanly.

---

## Project Directory Structure

```
Trust-Agent/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entry point & lifespan handlers
│   ├── agents/                  # [NEW] Orchestration Layer
│   │   ├── __init__.py
│   │   ├── pipeline.py          # AnalysisPipeline execution coordinator
│   │   └── trust_agent.py      # TrustAgent orchestrator class
│   ├── detectors/               # [NEW] Abstract Detector Contracts
│   │   ├── __init__.py
│   │   └── base.py             # BaseDetector contract & DetectorResult DTOs
│   ├── api/                     # REST API Presentation Layer
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependency Injection providers
│   │   └── v1/                  # API Version 1
│   │       ├── __init__.py
│   │       ├── router.py        # Central V1 API Router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── health.py    # Health check endpoint router
│   │           └── trust.py     # [NEW] POST /api/v1/trust/analyze router
│   ├── core/                    # Infrastructure & Cross-cutting Concerns
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic v2 settings & configuration
│   │   ├── exceptions.py        # Custom exceptions & global handlers
│   │   ├── logging.py           # Structured JSON/text logging engine
│   │   └── middleware.py        # Context tracing & CORS middleware
│   ├── schemas/                 # Data Transfer Objects & Pydantic Schemas
│   │   ├── __init__.py
│   │   ├── base.py              # Standard APIResponse[T] wrapper
│   │   ├── health.py            # Health payload schema
│   │   └── trust.py             # [NEW] TrustAnalysisRequest & TrustAnalysisResponse schemas
│   └── services/                # Abstract Business & Service Layer
│       ├── __init__.py
│       └── base.py              # Abstract BaseEngineService contract
├── tests/                       # Pytest Test Suite
│   ├── __init__.py
│   ├── conftest.py              # Async & Sync HTTP client fixtures
│   ├── test_health.py           # Health endpoint tests
│   └── test_trust.py            # [NEW] TrustAgent & /trust/analyze endpoint tests
├── .env.example                 # Environment variables configuration template
├── .gitignore                   # Git ignore rules
├── pyproject.toml               # Tool configuration & build metadata
├── requirements.txt             # Production dependencies
└── README.md                    # Project documentation
```

---

## Running the Server

Start the Uvicorn development server:
```bash
# Via uvicorn CLI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or directly via Python module
python -m app.main
```

---

## Testing

Execute the test suite using `pytest`:
```bash
pytest
```

---

## API Specification

### 1. `POST /api/v1/trust/analyze`

Executes trust evaluation pipeline for an incoming prompt.

**Request Body**:
```json
{
  "prompt": "Hello Trust Agent",
  "metadata": {
    "user_id": "user_123"
  }
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "request_id": "c71a39fa-5b23-42e1-93e1-381a1796d194",
    "timestamp": "2026-07-27T22:30:00.000000Z",
    "overall_status": "SAFE",
    "trust_score": 100.0,
    "findings": []
  },
  "error": null,
  "meta": {}
}
```

### 2. `GET /api/v1/health` (and `GET /health`)
Returns service health diagnostics.

---

## Orchestration Architecture

```
Client Request
      │
      ▼
POST /api/v1/trust/analyze
      │
      ▼
TrustAgent (Orchestrator)
      │
      ▼
AnalysisPipeline
      │
      ├──> BaseDetector 1 (e.g. Prompt Injection)
      ├──> BaseDetector 2 (e.g. PII)
      └──> BaseDetector N (e.g. Toxicity)
      │
      ▼
Aggregated TrustAnalysisResponse
```

---

## How to Add a New Detector

1. **Extend `BaseDetector`**:
   Create a new file in `app/detectors/`:
   ```python
   from app.detectors.base import BaseDetector, DetectorResult, FindingDetail, DetectorSeverity

   class PromptInjectionDetector(BaseDetector):
       @property
       def name(self) -> str:
           return "prompt_injection"

       @property
       def version(self) -> str:
           return "1.0.0"

       async def analyze(self, prompt: str, metadata: dict = None) -> DetectorResult:
           # Detection logic here
           return DetectorResult(detector_name=self.name, is_triggered=False, score=100.0)
   ```

2. **Register Detector with Pipeline**:
   Register in dependency provider (`app/api/deps.py`) or startup initializer:
   ```python
   pipeline = AnalysisPipeline()
   pipeline.register_detector(PromptInjectionDetector())
   ```
