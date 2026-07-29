import os
from pathlib import Path

BASE_DIR = Path("/home/pranav/Desktop/IntelliGaurd")

def fix_imports():
    # 1. backend/app/main.py
    main_py = BASE_DIR / "backend" / "app" / "main.py"
    if main_py.exists():
        content = main_py.read_text()
        content = content.replace("from app.api import security", "from backend.app.api import security")
        main_py.write_text(content)

    # 2. backend/app/api/security.py
    sec_py = BASE_DIR / "backend" / "app" / "api" / "security.py"
    if sec_py.exists():
        content = sec_py.read_text()
        content = content.replace("from agents.security_agent.agent import SecurityAgent", "from backend.agents.security_agent.agent import SecurityAgent, AgentResponse, AgentStatus")
        content = content.replace("from agents.security_agent.schemas import AnalyzeRequest", "from backend.agents.security_agent.models.communication import AnalyzeRequest")
        content = content.replace("from shared.response_models import AgentResponse\n", "")
        content = content.replace("from shared.enums import AgentStatus\n", "")
        sec_py.write_text(content)

    # 3. backend/agents/security_agent/tests/benchmark.py
    bench_py = BASE_DIR / "backend" / "agents" / "security_agent" / "tests" / "benchmark.py"
    if bench_py.exists():
        content = bench_py.read_text()
        content = content.replace("from agents.security_agent.agent import SecurityAgent", "from backend.agents.security_agent.agent import SecurityAgent")
        bench_py.write_text(content)

if __name__ == "__main__":
    fix_imports()
    print("Imports fixed.")
