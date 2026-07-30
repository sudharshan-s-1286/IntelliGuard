import json
import os
import re
from pathlib import Path

def categorize(text: str, source: str) -> str:
    t = text.lower()
    if re.search(r'\b(override|ignore|disregard|instead)\b', t):
        if re.search(r'\b(policy)\b', t):
            return "Policy Replacement"
        return "Instruction Override"
    elif re.search(r'\b(system prompt|instructions you were given|developer prompt)\b', t):
        return "System Prompt Extraction"
    elif re.search(r'\b(jailbreak|dan|do anything now|bypass)\b', t):
        return "Jailbreak"
    elif re.search(r'\b(role|you are now|act as|pretend to be)\b', t):
        return "Role Manipulation"
    elif re.search(r'\b(context|historical|previous|above)\b', t):
        return "Context Poisoning"
    elif re.search(r'\b(password|api key|secret|token|http|send|curl|wget)\b', t):
        return "Data Exfiltration"
    elif re.search(r'\b(tool|run|execute|command|bash|terminal|os)\b', t):
        return "Tool Abuse"
    elif re.search(r'\b(agent|workflow|orchestrator)\b', t):
        return "Agent Manipulation"
    else:
        return "Prompt Injection"

processed_dir = Path("datasets/processed")
count_total = 0
for filepath in processed_dir.glob("*.json"):
    with open(filepath, "r") as f:
        data = json.load(f)
    
    modified = False
    for record in data:
        if record.get("category") == "Extracted Pattern":
            new_cat = categorize(record.get("text", ""), record.get("source", ""))
            record["category"] = new_cat
            modified = True
            count_total += 1
            
    if modified:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {filepath.name}")

print(f"Total records updated: {count_total}")
