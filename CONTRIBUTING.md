# Contributing to IntelliGuard Enterprise Security Agent

Welcome to the IntelliGuard project! Please follow these guidelines when contributing code.

## Branch Naming Conventions
Use clear, descriptive branch names prefixed with the type of work being done:
- `feature/<feature-description>` (e.g., `feature/regex-timeout`)
- `bugfix/<bug-description>` (e.g., `bugfix/qdrant-connection`)
- `chore/<description>` (e.g., `chore/update-dependencies`)
- `docs/<description>` (e.g., `docs/update-architecture`)

## Pull Request Checklist
Before submitting a pull request, ensure you have completed the following:
- [ ] Code follows PEP 8 standards and uses proper type hints.
- [ ] The full test suite passes locally (`pytest backend/agents/security_agent/tests/`).
- [ ] Documentation has been updated if your changes affect architecture or public APIs.
- [ ] Commit history is reasonably clean and squashed if necessary.

## Testing Expectations
- Write unit tests for individual modules (`detectors`, `llm`, `reporting`).
- Write integration tests to ensure `agent.py` processes requests correctly.
- Test both positive (safe inputs) and negative (malicious/invalid inputs) paths.
