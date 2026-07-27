# Security Agent

The Security Agent is an enterprise-grade prompt analysis and remediation engine for the IntelliGuard multi-agent system. It is designed to proactively identify, score, and remediate prompt injection, role escalation, data exfiltration, and other LLM vulnerabilities before they reach downstream models.

## Integration Contract & Public Interface

The Security Agent implements the standard `BaseAgent` interface located in `backend/shared/interfaces.py`, ensuring seamless compatibility with the future Orchestrator Agent. 

It exposes the following public methods:
- `process(request)`: The primary entry point. Parses, detects, scores, remediates, audits, and returns an `AgentResponse`.
- `health()`: Checks the status of the detector, scorer, audit, and remediation subcomponents.
- `ready()`: Verifies that configurations, patterns, and rewrite templates are properly loaded into memory.
- `capabilities()`: Broadcasts supported attack detections (e.g., Prompt Injection, Jailbreak) and core features.
- `metrics()`: Exposes live operational statistics including `total_requests`, `failed_requests`, and `average_processing_time_ms`.
- `version()`: Returns the current semantic version of the agent.

## Communication Flow & Agent Lifecycle

Every incoming request follows a strict, sequential lifecycle:
1. **Validation & Normalization** (`prompt_parser.py`): The raw prompt is sanitized, whitespace is normalized, and basic encodings are decoded.
2. **Threat Detection** (`detector.py`): The payload is scanned concurrently against dozens of regex and heuristic signatures defined in `patterns.py`.
3. **Risk Assessment** (`scorer.py`): An explainable engine aggregates the findings, applying weighted thresholds (from `config.py`) to generate a `risk_score` (0-100) and severity category.
4. **Decision Engine** (`decision.py`): Outputs a declarative directive (`ALLOW`, `WARN`, `MODIFY`, or `BLOCK`) and generates human-readable XAI justifications.
5. **Remediation Engine** (`remediation.py`): If the prompt is malicious, this engine actively rewrites it into a safe, educational alternative using `REWRITE_TEMPLATES`.
6. **Audit Logging** (`audit/logger.py`): The entire pipeline trace is persisted securely as a JSON `AuditEvent` without blocking the main response thread.
7. **Response Wrapping**: The final payload is packaged into a standardized `AgentResponse` JSON block and returned to the Orchestrator or API client.

## Extension Points

The architecture is highly modular to support future LLM integrations:
- **Custom Detectors**: New attack vectors can be added to `patterns.py` without modifying core logic. Advanced AI-based detectors can implement the same signature interface in `detector.py`.
- **Custom Scoring**: Weights and multipliers can be seamlessly tuned in `config.py` without modifying the core assessment algorithms.
- **Audit Storage**: Currently uses local JSON files via `audit/storage.py`, but can easily be subclassed to integrate with PostgreSQL, MongoDB, or Elasticsearch for SIEM aggregation.
