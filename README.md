# Enterprise AI Security Agent

IntelliGuard Enterprise AI Security Agent is a specialized security platform that detects and mitigates prompt injections, jailbreaks, data exfiltration attempts, and other adversarial attacks against enterprise AI models.

## Features
- **Semantic Detection Engine**: Uses Qdrant vector database for semantic similarity detection of known adversarial prompts.
- **Decision Engine**: Orchestrates standard detection pipelines and decides if LLM fallback is needed.
- **LLM Classifier Fallback**: Acts as the ultimate arbiter for ambiguous or zero-day threats.
- **Risk Scorer**: Computes robust numerical risk profiles based on confidence, severity, and attack type.
- **Report Generator**: Standardizes outputs for enterprise logging and mitigation strategies.

## Setup
See `DEVELOPMENT_GUIDE.md` for local setup.
