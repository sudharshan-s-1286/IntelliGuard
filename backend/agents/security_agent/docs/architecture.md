# Security Agent Architecture

The IntelliGuard Security Agent is an enterprise-ready pipeline designed to analyze AI prompts and payloads for security threats (like Prompt Injection, Jailbreaks, and PII leaks). It employs a robust hybrid architecture, combining lightning-fast rule matching, semantic vector search, and a highly-capable LLM fallback for ambiguous cases.

## Core Pipeline

When an API client sends a prompt to the `SecurityAgent.process()` method, it flows through the following asynchronous stages:

1. **Input Normalization (`request_validator.py`)**: Sanitizes and normalizes the raw prompt, flagging standard obfuscations (Base64, Hex).
2. **Decision Engine Orchestration (`decision_engine.py`)**: 
   - **Rule Engine**: Synchronously executes hundreds of RegEx and heuristic rules.
   - **Semantic Detector**: Concurrently queries a `Qdrant` vector database for semantic similarity against historical known attacks.
   - **Merging**: Duplicates are merged, confidences are fused, and severities are aggregated.
3. **LLM Fallback (`llm/classifier.py`)**: If the `DecisionEngine` identifies ambiguous findings (low confidence) or conflicts between the Rule Engine and Semantic Detector, the prompt and prior findings are sent to the `LLMClassifier` for an expert tie-breaking decision.
4. **Risk Assessment (`risk_scorer.py`)**: Findings are aggregated and weighted based on source (LLM hits hold higher weight than generic RegEx), severity, and multiplier penalties (e.g. encoded payloads), generating a final `RiskScore` out of 100.
5. **Report Generation (`reporting/generator.py`)**: The `DetectionResult` is converted into a standard `SecurityAgentResponse` compatible with the broader IntelliGuard API format, including structured explainability.

## Key Subsystems

### Telemetry & Auditing
- **Audit Logger**: Outputs structured enterprise audit trails (Trace IDs, timestamps, detection types, latency).
- **Metrics Registry**: In-memory registry measuring throughput, cache hit rates, error counts, and API response times. Hooked directly into the `/health` endpoint.

### LLM Abstraction
- The `LLMClassifier` utilizes a robust `LLMProvider` abstraction (`providers.py`).
- Supports an `OpenAIProvider` with `AsyncOpenAI`.
- Includes a `MockProvider` for seamless local testing and graceful fallback when API keys are unconfigured.

## Deployment Configuration

Configure the agent via environment variables (defined in `settings.py`):

| Variable | Description | Default |
| --- | --- | --- |
| `QDRANT_HOST` | Host URL for the Qdrant DB | `localhost` |
| `LLM_PROVIDER` | `openai`, `azure`, `anthropic`, `mock` | `mock` |
| `LLM_API_KEY` | Provider API Key | `""` |
| `LLM_MODEL_NAME` | The model to use | `gpt-4-turbo` |
| `LLM_TIMEOUT` | Max execution time for LLM call | `5.0` |
| `DECISION_LLM_ROUTING_THRESHOLD` | Confidence below this triggers LLM | `0.6` |

## Error Handling
The agent is designed to never crash the main application thread. Failures in external dependencies (Qdrant, LLM API) trigger built-in timeout bounds, automatic retries, and safe fallback values ("Unknown", Safe default).
