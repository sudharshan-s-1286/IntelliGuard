# IntelliGuard Security Agent

This is the Security Agent for the IntelliGuard platform. It implements a hybrid detection pipeline:
- **Rule Engine**: Fast regex/pattern heuristics.
- **Semantic Detector**: Vector similarity search via Qdrant.
- **LLM Classifier**: Fallback classification using powerful LLMs.

## Architecture
The agent follows a strict layered architecture:
- `detectors/`: Threat identification logic.
- `ai/`: AI model management and embeddings.
- `knowledge/`: Attack pattern lifecycle.
- `repositories/`: Vector DB interactions.
- `services/`: Cross-cutting business logic.
- `models/`: Domain schemas.
