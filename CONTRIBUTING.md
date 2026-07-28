# Contributing to IntelliGuard

Welcome to the IntelliGuard project! To ensure smooth collaboration across all teams developing the multi-agent AI governance platform, please follow these guidelines when contributing code.

## Branch Naming Conventions
Use clear, descriptive branch names prefixed with the type of work being done:
- `feature/<agent-name>-<feature-description>` (e.g., `feature/privacy-agent-data-masking`)
- `bugfix/<agent-name>-<bug-description>` (e.g., `bugfix/security-agent-regex-timeout`)
- `chore/<description>` (e.g., `chore/update-dependencies`)
- `docs/<description>` (e.g., `docs/update-architecture-guidelines`)

## Commit Message Guidelines
Write clear, concise commit messages that describe the *what* and *why* of your changes.
- Use the imperative mood (e.g., "Add privacy detection logic" not "Added..." or "Adds...").
- Keep the first line under 50 characters.
- Add detailed explanations in the body if necessary, separated by a blank line.
- Reference issue or ticket numbers when applicable.

## Pull Request Checklist
Before submitting a pull request, ensure you have completed the following:
- [ ] Code follows PEP 8 standards and uses proper type hints.
- [ ] No agent isolation boundaries have been crossed (you only used public interfaces).
- [ ] Tests are written and reside exclusively in your agent's `tests/` directory.
- [ ] The full test suite passes locally.
- [ ] Documentation has been updated if your changes affect architecture or public APIs.
- [ ] Commit history is reasonably clean and squashed if necessary.

## Code Review Expectations
- Reviewers will check for strict adherence to the agent architecture rules. Direct imports of another agent's internal modules will be rejected.
- Expect feedback on security, performance, and maintainability.
- Resolve all comments and receive at least one approval from a core maintainer before merging.

## Testing Expectations
- Every agent is responsible for its own test coverage.
- Write unit tests for individual modules (`detector`, `scorer`, `decision`).
- Write integration tests to ensure your `agent.py` processes requests correctly.
- Test both positive (safe inputs) and negative (malicious/invalid inputs) paths.
- Ensure your tests do not rely on another agent's private state or mock internal functions of other agents.

## Merge Conflict Resolution Tips
Because the architecture is heavily isolated by agent, merge conflicts should be rare. If they occur:
1. **In `app/main.py`**: Usually caused by multiple agents registering routers simultaneously. Carefully merge the router inclusions.
2. **In `shared/`**: Discuss changes with the team before modifying shared interfaces to ensure you aren't breaking other agents.
3. **In `requirements.txt`**: Ensure all newly added dependencies are compatible with the existing ecosystem.
Always pull the latest changes from the `main` branch and rebase/merge locally to resolve conflicts before requesting a review.
