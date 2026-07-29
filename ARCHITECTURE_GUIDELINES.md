# Enterprise AI Security Agent Architecture Guidelines

## 1. Project Overview
IntelliGuard is a state-of-the-art Enterprise AI Security Agent. It is designed to ensure safety and trust across all AI interactions by mitigating prompt injections, jailbreaks, and adversarial attacks against AI models. 

### Core Components:
- **Security Agent**: The facade entry point containing all orchestration logic for the security pipeline.
- **Rule Engine**: Evaluates prompt patterns against hardcoded regular expressions.
- **Semantic Detector**: Utilizes embeddings and Qdrant to search for semantic similarities to known attacks.
- **Decision Engine**: Orchestrates the Rule Engine and Semantic Detector, determining if the LLM Classifier must be invoked.
- **LLM Classifier**: Analyzes ambiguous prompts as a fallback mechanism.
- **Risk Scorer & Report Generator**: Computes the final numerical risk and standardizes the output.

## 2. Project Folder Structure
The backend follows a scalable, domain-driven architecture:

```text
backend/
├── agents/
│   └── security_agent/    # Core implementation of the Security Agent
└── requirements.txt       # Global Python dependencies
```

## 3. Security Agent Internal Structure
```text
security_agent/
├── agent.py         # Main entry point (SecurityAgent facade)
├── detectors/       # Detection logic (Semantic, Rule, Decision Engines)
├── llm/             # LLM Classifier fallback logic
├── reporting/       # Report and response generation
├── config/          # Configurations and constants
├── utils/           # Helper functions (Telemetry, AuditLogging)
├── models/          # Data models and schemas
├── repositories/    # Qdrant Knowledge Base and storage
└── tests/           # Unit and integration tests
```

## 4. Coding Standards
- **Use type hints**: All function signatures must include Python type hints for arguments and return types.
- **Follow PEP 8**: Adhere to standard Python style guidelines (use tools like `ruff` or `flake8`).
- **Single Responsibility Principle**: Keep functions focused on a single responsibility.
