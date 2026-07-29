import os
import re

base_dir = "/home/pranav/Desktop/IntelliGaurd/backend/agents/security_agent"

def replace_in_file(filepath, pattern, replacement):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r') as f:
        content = f.read()
    content = re.sub(pattern, replacement, content)
    with open(filepath, 'w') as f:
        f.write(content)

# 1. Update Test Imports
tests_dir = os.path.join(base_dir, "tests")

# test_api.py
replace_in_file(os.path.join(tests_dir, "test_api.py"), 
                r'agents\.security_agent\.schemas', 
                r'backend.shared.models.communication')

# test_scorer.py
replace_in_file(os.path.join(tests_dir, "test_scorer.py"), 
                r'from agents\.security_agent\.scorer import calculate_risk_score', 
                r'from backend.agents.security_agent.detectors.risk_scorer import calculate_risk_score')

# test_decision.py
replace_in_file(os.path.join(tests_dir, "test_decision.py"), 
                r'from agents\.security_agent\.decision import make_decision', 
                r'from backend.agents.security_agent.detectors.decision_engine import make_decision')

# test_remediation.py
replace_in_file(os.path.join(tests_dir, "test_remediation.py"), 
                r'from agents\.security_agent\.remediation import remediate', 
                r'from backend.agents.security_agent.services.remediation_service import remediate')

# 2. Refactor Scorer -> RiskScorer
with open(os.path.join(base_dir, "scorer.py"), "r") as f:
    scorer_code = f.read()
scorer_code = scorer_code.replace("from .config import", "from backend.agents.security_agent.config.settings import")
with open(os.path.join(base_dir, "detectors", "risk_scorer.py"), "w") as f:
    f.write(scorer_code)

# 3. Refactor Decision -> DecisionEngine
with open(os.path.join(base_dir, "decision.py"), "r") as f:
    decision_code = f.read()
decision_code = decision_code.replace("from .config import", "from backend.agents.security_agent.config.settings import")
with open(os.path.join(base_dir, "detectors", "decision_engine.py"), "w") as f:
    f.write(decision_code)

# 4. Refactor Remediation -> RemediationService
with open(os.path.join(base_dir, "remediation.py"), "r") as f:
    remediation_code = f.read()
remediation_code = remediation_code.replace("from .config import", "from backend.agents.security_agent.config.settings import")
with open(os.path.join(base_dir, "services", "remediation_service.py"), "w") as f:
    f.write(remediation_code)

# 5. Refactor Detector -> RuleEngine
with open(os.path.join(base_dir, "detector.py"), "r") as f:
    detector_code = f.read()
detector_code = detector_code.replace("from .patterns import", "from backend.agents.security_agent.knowledge.manager import")
detector_code = detector_code.replace("from .utils import", "from backend.agents.security_agent.validators.request_validator import")
with open(os.path.join(base_dir, "detectors", "rule_engine.py"), "w") as f:
    f.write(detector_code)

# 6. Refactor Utils -> RequestValidator
with open(os.path.join(base_dir, "utils.py"), "r") as f:
    utils_code = f.read()
with open(os.path.join(base_dir, "validators", "request_validator.py"), "w") as f:
    f.write(utils_code)

# 7. Refactor Patterns -> Knowledge Manager
with open(os.path.join(base_dir, "patterns.py"), "r") as f:
    patterns_code = f.read()
with open(os.path.join(base_dir, "knowledge", "manager.py"), "w") as f:
    f.write(patterns_code)

# Delete Legacy Root Files
legacy_files = ['scorer.py', 'decision.py', 'remediation.py', 'detector.py', 'utils.py', 'patterns.py', 'prompt_parser.py', 'config.py']
for lf in legacy_files:
    lf_path = os.path.join(base_dir, lf)
    if os.path.exists(lf_path):
        os.remove(lf_path)
