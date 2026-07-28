# IntelliGuard Development Guide

Welcome to the IntelliGuard developer onboarding guide! This document covers the essential steps for setting up, running, and expanding the backend architecture.

## 1. Backend Setup & Dependencies
Ensure you have Python 3.10+ installed.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Starting the FastAPI Server
The IntelliGuard backend is built using FastAPI. To start the local development server:

```bash
fastapi dev app/main.py
# Alternatively: uvicorn app.main:app --reload
```
The server will start on `http://127.0.0.1:8000`. You can view the interactive API documentation at `http://127.0.0.1:8000/docs`.

## 3. Running Tests
The project relies on `pytest`. All tests are isolated within each agent's respective folder.

To run tests for the Trust Agent:
```bash
python3 -m pytest agents/trust_agent/tests/
```
Ensure your virtual environment is active before running tests.

## 4. How to Add a New Agent
IntelliGuard is designed for modular scalability. To create a new agent:

1. **Create the Folder**: Create a new directory under `agents/` (e.g., `agents/risk_agent/`).
2. **Implement the Agent**: Create `agent.py` and implement the `BaseAgent` interface from `shared.interfaces`.
3. **Follow the Structure**: Add `detector.py`, `scorer.py`, `models.py`, etc., as needed for your domain.
4. **Isolate Tests**: Create `agents/risk_agent/tests/` and place all unit and integration tests there.
5. **Standardize Output**: Ensure your `process()` method returns an `AgentResponse` from `shared.response_models`.

## 5. Exposing a New API Endpoint
Once your agent is built, you need to expose it through the Orchestrator (API layer).

1. **Create a Router**: Create a new file in `app/api/` (e.g., `app/api/risk.py`).
2. **Define Endpoints**: Use FastAPI's `APIRouter` to define your endpoints. Instatiate your agent and call `agent.process()`.
   *Remember: Do not import internal agent modules (like `schemas.py` or `detector.py`) into the API layer.*
3. **Register Router**: Open `app/main.py` and include your new router:
   ```python
   from app.api import risk
   app.include_router(risk.router)
   ```

## 6. Common Project Conventions
- **Public Interfaces Only**: Never import another agent's internal modules. Use only what is exposed in `agent.py`.
- **Shared Folder Limits**: Only put genuinely reusable components in `shared/`. Do not pollute it with agent-specific logic.
- **Type Hinting**: All functions should use comprehensive Python type hinting.
- **Response Format**: Always adhere to the `AgentResponse` envelope.
