# IntelliGuard Testing Suite

This repository contains the comprehensive CI/CD testing suite for the Security Agent.

## Test Categories

1. **Unit Tests** (`tests/unit/`): Validates individual internal components (Parser, Detector, Scorer, Remediation, Audit).
2. **Integration Tests** (`tests/integration/`): Tests the end-to-end multi-agent orchestration pipeline data flow.
3. **API Tests** (`tests/api/`): Tests FastAPI REST endpoints with valid and malformed requests using `TestClient`.
4. **Security & Threat Tests** (`tests/security/`):
    - `test_threats.py`: Dedicated payloads for all 10+ attack vectors (Injection, Jailbreak, Exfiltration, etc.).
    - `test_edge_cases.py`: Checks for resilience against 15,000+ char strings, Unicode emojis, SQL injections, and encoded attacks.
    - `test_errors.py`: Validates that simulated infrastructure failures (e.g. Audit Storage crashes) do not break the main inference loop.
5. **Performance Tests** (`tests/performance/`): Verifies throughput and latency requirements using multi-threading.

## Running the Tests

To run the full suite automatically, use the provided shell script from the `backend/` directory:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Expected Output
- `pytest` will execute all Unit, API, Integration, and Security tests.
- A coverage report (`term-missing`) will guarantee >90% code coverage.
- The performance benchmark will simulate 100, 500, and 1,000 concurrent threads to ensure average latency remains <200ms.
- All results are piped into `test_report.txt`.
