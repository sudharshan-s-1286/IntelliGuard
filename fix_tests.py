import os
import re

base_dir = "/home/pranav/Desktop/IntelliGaurd/backend/agents/security_agent"
tests_dir = os.path.join(base_dir, "tests")

def replace_in_file(filepath, pattern, replacement):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r') as f:
        content = f.read()
    content = re.sub(pattern, replacement, content)
    with open(filepath, 'w') as f:
        f.write(content)

# Update remaining test imports
replace_in_file(os.path.join(tests_dir, "test_detector.py"), 
                r'from agents\.security_agent\.detector import', 
                r'from backend.agents.security_agent.detectors.rule_engine import')

replace_in_file(os.path.join(tests_dir, "test_parser.py"), 
                r'from agents\.security_agent\.prompt_parser import', 
                r'from backend.agents.security_agent.validators.request_validator import')

replace_in_file(os.path.join(tests_dir, "test_audit.py"), 
                r'from agents\.security_agent\.audit', 
                r'from backend.agents.security_agent.audit')

replace_in_file(os.path.join(tests_dir, "test_decision.py"), 
                r'from agents\.security_agent\.decision', 
                r'from backend.agents.security_agent.detectors.decision_engine')
