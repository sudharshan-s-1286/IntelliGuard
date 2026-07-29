# IntelliGuard Development Guide

Welcome to the IntelliGuard developer onboarding guide! This document covers the essential steps for setting up and running the Enterprise Security Agent.

## 1. Backend Setup & Dependencies
Ensure you have Python 3.10+ installed.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Running Tests
The project relies on `pytest`. 

To run tests for the Security Agent:
```bash
python3 -m pytest agents/security_agent/tests/
```
Ensure your virtual environment is active and PYTHONPATH is set to the root directory before running tests.

## 3. Core Entry Point
The agent is encapsulated inside `backend/agents/security_agent/agent.py`. It exposes an async `initialize()` method for starting external connections (like Qdrant) and an async `process()` method for evaluating prompts.
