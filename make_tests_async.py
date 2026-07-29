import os
import re

tests_dir = "/home/pranav/Desktop/IntelliGaurd/backend/agents/security_agent/tests"

def make_tests_async(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        content = f.read()

    # Add pytest mark
    if "pytest.mark.asyncio" not in content and "def test_" in content:
        if "import pytest" not in content:
            content = "import pytest\n" + content
        
        # Replace def test_ with @pytest.mark.asyncio\nasync def test_
        content = re.sub(r'def test_([a-zA-Z0-9_]+)\(', r'@pytest.mark.asyncio\nasync def test_\1(', content)

        # Replace agent.process() with await agent.process()
        content = content.replace("agent.process(", "await agent.process(")
        
        # Replace agent.analyze() with await agent.analyze()
        content = content.replace("agent.analyze(", "await agent.analyze(")
        
        # Replace get_decision() with await get_decision() in test_threats
        content = content.replace("res = get_decision(", "res = await get_decision(")
        content = content.replace("def get_decision", "async def get_decision")
        content = content.replace("agent.analyze(prompt)", "await agent.analyze(prompt)")

        # Fix mocks in test_errors.py
        if "test_errors.py" in filepath:
            content = content.replace('agents.security_agent.agent.run_all_detectors', 'backend.agents.security_agent.detectors.rule_engine.run_all_detectors')
            content = content.replace('import agents.security_agent.agent', 'import backend.agents.security_agent.agent')
            content = content.replace('monkeypatch.setattr(agents.security_agent.agent,', 'monkeypatch.setattr(backend.agents.security_agent.agent,')

        with open(filepath, "w") as f:
            f.write(content)

for filename in os.listdir(tests_dir):
    if filename.endswith(".py") and filename.startswith("test_"):
        make_tests_async(os.path.join(tests_dir, filename))
