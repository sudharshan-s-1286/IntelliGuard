# IntelliGuard Architecture Guidelines

## 1. Project Overview
IntelliGuard is a state-of-the-art enterprise multi-agent AI governance platform. It is designed to ensure safety, compliance, privacy, and trust across all AI interactions. The platform is modular, consisting of multiple specialized AI agents orchestrated by a central component.

### Agent Purposes:
- **Trust Agent**: Evaluates the reliability, factuality, and lack of bias in AI-generated responses. This is the sole active AI agent in the system.
- **Orchestrator**: The central controller that routes requests, manages the lifecycle of agent execution, aggregates results, and enforces global decision policies.

## 2. Project Folder Structure
The backend follows a scalable, domain-driven architecture:

```text
backend/
├── app/               # FastAPI application, core settings, and API routers (The Orchestrator layer)
├── agents/            # Isolated implementation of each AI agent
├── shared/            # Reusable components, base interfaces, and standard models
└── requirements.txt   # Global Python dependencies
```

### Responsibilities
- **`app/`**: Handles the web server, request routing, dependency injection, and middleware. It orchestrates calls to the agents.
- **`agents/`**: Contains subdirectories for each agent (e.g., `trust_agent`). Each folder is a self-contained domain.
- **`shared/`**: Contains cross-cutting concerns that multiple agents rely on, preventing duplicate code while maintaining strict separation.

## 3. Agent Structure Standard
Every agent must follow a standardized directory layout to ensure consistency and maintainability across the team.

```text
agent_name/
├── __init__.py
├── agent.py         # The main entry point implementing BaseAgent
├── detector.py      # Core detection/analysis logic
├── scorer.py        # Risk or confidence scoring mechanisms
├── decision.py      # Logic for making ALLOW/BLOCK/MODIFY decisions
├── remediation.py   # (Optional) Logic for applying fixes to prompts
├── patterns.py      # (Optional) Regex signatures or rule definitions
├── models.py        # Internal data models and database schemas
├── schemas.py       # Pydantic validation schemas for internal use
├── config.py        # Agent-specific configuration and constants
├── utils.py         # Agent-specific helper functions
├── tests/           # All unit, integration, and security tests for this agent
└── README.md        # Documentation for the agent's specific capabilities
```
*Note: Files marked as optional (like `remediation.py` or `patterns.py`) may be omitted if the agent does not require that functionality.*

## 4. Public Interface Rules
To maintain strict boundaries and avoid spaghetti code, **every agent must expose only a single public interface**, typically the `process()` method defined in `agent.py`.

- The `app/` layer (Orchestrator) and other services must **only** interact with the agent via `AgentName.process()`.
- Internal modules such as `detector.py`, `scorer.py`, `patterns.py`, or `schemas.py` **must not** be accessed or imported directly by anything outside of the agent's own folder.

## 5. Shared Components
The `shared/` directory is exclusively for cross-cutting, reusable components. Agent-specific logic must **never** be placed here.

### Examples of what belongs in `shared/`:
- **Base classes**: `BaseAgent` (the abstract class all agents implement).
- **Common interfaces**: standardized payload signatures.
- **Shared response models**: `AgentResponse`, ensuring every agent returns the exact same envelope (e.g., status, processing_time, metadata).
- **Logging utilities**: Standardized formatters or tracing setups.
- **Common exceptions**: Global exception handlers.
- **Shared helper functions**: Generic utilities (e.g., date parsing, hashing) that do not contain domain logic.

## 6. Team Development Rules
When collaborating on IntelliGuard, strictly adhere to the following rules to prevent merge conflicts and architectural degradation:
- **Do not modify another team's agent internals.** If you need functionality from another agent, request a feature or use its public interface.
- **Only interact with another agent through its public interface.**
- **Keep tests inside each agent's `tests/` folder.** Do not place agent-specific unit tests in a global `tests/` directory.
- **Avoid circular imports.** Ensure the dependency graph flows one way (e.g., `app/` -> `agents/` -> `shared/`).
- **Follow consistent naming conventions.** Prefix agent-specific modules correctly and use clear, descriptive variable names.

## 7. Coding Standards
- **Use type hints**: All function signatures must include Python type hints for arguments and return types.
- **Follow PEP 8**: Adhere to standard Python style guidelines (use tools like `ruff` or `flake8`).
- **Single Responsibility Principle**: Keep functions focused on a single responsibility. If a function does two things, split it.
- **Maintain consistent naming**: Classes use `PascalCase`, functions and variables use `snake_case`, constants use `UPPER_SNAKE_CASE`.

## 8. Future Expansion
The architecture is designed to seamlessly scale. New agents (e.g., `BiasAgent`, `RiskAgent`, `AuditAgent`) can be added without modifying existing architecture:
1. Create a new folder in `agents/` (e.g., `agents/bias_agent/`).
2. Implement the `BaseAgent` interface in `agent.py`.
3. Build the internal logic (`detector.py`, `scorer.py`, etc.).
4. Add the agent's unit tests to `agents/bias_agent/tests/`.
5. Expose the new agent in `app/api/bias.py` and register the router in `app/main.py`.
By adhering to the `BaseAgent` contract and standardized `AgentResponse`, the Orchestrator will automatically support the new agent.
