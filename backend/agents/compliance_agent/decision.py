import os
import yaml
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PolicyEngine:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to the app/config/compliance_rules.yaml
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config", "compliance_rules.yaml")
            
        self.config_path = config_path
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("rules", [])
        except FileNotFoundError:
            logger.error(f"Policy rules file not found at {self.config_path}")
            return []
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML from {self.config_path}: {e}")
            return []

    def evaluate(self, context: Dict[str, Any], findings: List[str]) -> List[Dict[str, Any]]:
        """
        Evaluate context and findings against loaded rules.
        Returns a list of violated rules.
        """
        violated_rules = []
        
        # Normalize findings to lowercase for case-insensitive matching
        normalized_findings = [f.lower() for f in findings]
        
        for rule in self.rules:
            # Assume rule is violated until proven otherwise based on defined conditions
            violated = True
            
            # Check context constraints (like 'role')
            for key, expected_value in rule.items():
                if key in ["id", "severity", "contains"]:
                    continue # Not context attributes
                    
                context_val = context.get(key)
                # If context doesn't match the required rule value, rule is not violated
                if str(context_val).lower() != str(expected_value).lower():
                    violated = False
                    break
                    
            if not violated:
                continue
                
            # Check findings constraint ('contains')
            if "contains" in rule:
                contains_val = str(rule["contains"]).lower()
                # Check if the required 'contains' string is present in any of the findings
                found = any(contains_val in f for f in normalized_findings)
                if not found:
                    violated = False
            
            if violated:
                logger.info(f"Rule {rule.get('id')} violated.")
                violated_rules.append(rule)
                
        return violated_rules
