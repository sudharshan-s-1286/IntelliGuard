import logging
import re
from typing import Dict, List, Any, Optional
from shared.base_agent import BaseDetector

logger = logging.getLogger(__name__)

# Default regex patterns and severities for confidential data
DEFAULT_CONFIDENTIAL_PATTERNS: Dict[str, Dict[str, str]] = {
    "AWS_ACCESS_KEY": {
        "pattern": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
        "severity": "CRITICAL",
    },
    "JWT_TOKEN": {
        "pattern": r"\beyJ[A-Za-z0-9-_=]{10,2048}\.[A-Za-z0-9-_=]{1,2048}\.[A-Za-z0-9-_.+/=]{1,2048}\b",
        "severity": "HIGH",
    },
    "BEARER_TOKEN": {
        "pattern": r"(?i:\bbearer\s+[A-Za-z0-9-._~+/]{10,2048}=*\b)",
        "severity": "HIGH",
    },
    "API_KEY": {
        "pattern": r"\bsk_(?:live|test)_[0-9a-zA-Z]{24,32}\b|(?i:\b(?:api_key|apikey|x-api-key)\b\s*[:=]\s*[\"']?[a-zA-Z0-9_\-]{16,64}[\"']?)",
        "severity": "HIGH",
    },
    "SSH_KEY": {
        "pattern": r"-----BEGIN[ A-Z]{1,30}PRIVATE KEY-----[\s\S]{10,5000}?-----END[ A-Z]{1,30}PRIVATE KEY-----",
        "severity": "CRITICAL",
    },
    "PASSWORD": {
        "pattern": r"(?i:\b(?:password|passwd|pwd)\b\s*[:=]\s*[\"']?[a-zA-Z0-9@#$%^&*()_+!\-]{6,30}[\"']?)",
        "severity": "HIGH",
    },
    "SECRET": {
        "pattern": r"(?i:\b(?:secret|secret_key|client_secret)\b\s*[:=]\s*[\"']?[a-zA-Z0-9_\-]{16,64}[\"']?)",
        "severity": "HIGH",
    },
    "DB_CONNECTION_STRING": {
        "pattern": r"\b(?:mongodb|postgres|postgresql|mysql|mssql|oracle|redshift|db2)://[a-zA-Z0-9_.-]{1,128}(?::[a-zA-Z0-9_.-]{1,128})?@[a-zA-Z0-9_.-]{1,255}(?::\d{1,5})?(?:/[a-zA-Z0-9_.-]{0,128})?",
        "severity": "CRITICAL",
    },
}


class ConfidentialDetector(BaseDetector):
    """
    Detector responsible for identifying sensitive credentials and confidential tokens
    (such as AWS access keys, JWT tokens, private SSH keys, and db connection strings)
    within text content using regular expression patterns.
    """

    def __init__(self, custom_patterns: Optional[Dict[str, Dict[str, str]]] = None) -> None:
        """
        Initializes the ConfidentialDetector with default or custom patterns.

        Args:
            custom_patterns: A dictionary mapping secret types (e.g., 'JWT_TOKEN') to dictionaries
                             containing 'pattern' (regex string) and optionally 'severity' (str).
        """
        self.patterns: Dict[str, Dict[str, str]] = {}
        for key, val in DEFAULT_CONFIDENTIAL_PATTERNS.items():
            self.patterns[key] = {
                "pattern": val["pattern"],
                "severity": val["severity"],
            }

        # Override or add custom patterns
        if custom_patterns:
            for key, val in custom_patterns.items():
                if "pattern" in val:
                    self.patterns[key] = {
                        "pattern": val["pattern"],
                        "severity": val.get("severity", "HIGH"),
                    }
            logger.info("ConfidentialDetector initialized with custom patterns.")
        else:
            logger.info("ConfidentialDetector initialized with default patterns.")

        # Precompile patterns for runtime efficiency
        self.compiled_patterns = {
            key: re.compile(val["pattern"])
            for key, val in self.patterns.items()
        }

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans input text for matches against compiled confidential data patterns.
        Resolves overlapping findings by prioritizing longer match spans.

        Args:
            text: The raw text content to analyze.

        Returns:
            A list of dictionary findings, where each finding has:
            - 'type': Confidential data type name (str)
            - 'severity': Severity level (str)
            - 'text': The matched substring (str)
        """
        findings: List[Dict[str, Any]] = []
        if not text:
            logger.debug("Empty text provided to ConfidentialDetector. Returning empty list.")
            return findings

        # Collect all raw matches across all patterns
        raw_findings: List[Dict[str, Any]] = []
        for secret_type, compiled_regex in self.compiled_patterns.items():
            severity = self.patterns[secret_type]["severity"]
            for match in compiled_regex.finditer(text):
                raw_findings.append({
                    "type": secret_type,
                    "severity": severity,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                })

        if raw_findings:
            logger.info(f"Found {len(raw_findings)} potential confidential matches before deduplication.")

        from shared.utils import remove_overlapping_spans
        findings = remove_overlapping_spans(raw_findings)

        if findings:
            logger.warning(f"Detected {len(findings)} confidential data violations.")

        return findings


import re
import logging
from typing import List, Dict, Any
from shared.base_agent import BaseDetector

logger = logging.getLogger(__name__)

class CopyrightDetector(BaseDetector):
    def __init__(self):
        super().__init__()
        # Define regex patterns for copyright and license violations
        self.patterns = {
            "License-sensitive code": [
                r"(?i)\b(?:GNU General Public License|GPL|AGPL|LGPL)\b",
                r"(?i)\b(?:Apache License(?:,?\s*Version\s*\d\.\d)?)\b",
                r"(?i)\b(?:MIT License)\b",
                r"(?i)\b(?:BSD\s*\d?-Clause(?: \w+)? License)\b",
                r"(?i)\b(?:Mozilla Public License|MPL)\b"
            ],
            "Copyright warnings": [
                r"(?i)copyright\s+(?:\(c\)\s+|©\s+)?(?:\d{4}-?\d{0,4}\s+)?(?:by\s+)?[\w\s,]+",
                r"(?i)all rights reserved"
            ],
            "Large copied passages": [
                # Matches a blockquote of 3 or more lines
                r"(?:^>\s*.*$\n?){3,}",
                # Matches very long strings inside quotes (over 200 chars)
                r"(?:\"|').{200,}(?:\"|')"
            ],
            "Excessive quotations": [
                # Matches if there are more than 4 sets of quotes in a relatively short span, simplified to just a large number of quotes globally in text.
                # Actually, we can just use a pattern that matches 4 separate quoted strings closely together.
                r"(?:(?:\"[^\"]+\"|'[^']+')(?:\s*.*?){0,50}){4,}"
            ]
        }
        
        # Compile all regexes
        self.compiled_rules = []
        for issue_type, patterns in self.patterns.items():
            for pattern in patterns:
                # Use MULTILINE so ^ matches start of a line
                self.compiled_rules.append((issue_type, re.compile(pattern, re.MULTILINE)))

    def detect(self, text: str) -> List[Dict[str, Any]]:
        findings = []
        if not text:
            return findings

        # Collect all raw matches across all patterns
        raw_findings: List[Dict[str, Any]] = []
        for issue_type, regex in self.compiled_rules:
            for match in regex.finditer(text):
                raw_findings.append({
                    "issue_type": issue_type,
                    "matched": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                })

        from shared.utils import remove_overlapping_spans
        deduped = remove_overlapping_spans(raw_findings)
        
        for f in deduped:
            findings.append({
                "issue": "Possible copyrighted content",
                "severity": "Low",
                "details": f["issue_type"],
                "matched": f["matched"]
            })
            logger.info(f"CopyrightDetector found {f['issue_type']}: {f['matched'][:50]}...")
            
        return findings


import re
from typing import Dict, List, Any, Optional

# Default regex patterns and severities for PII detection
DEFAULT_PATTERNS: Dict[str, Dict[str, str]] = {
    "EMAIL": {
        "pattern": r"\b[a-zA-Z0-9._%+-]{1,64}@[a-zA-Z0-9.-]{1,255}\.[a-zA-Z]{2,63}\b",
        "severity": "HIGH",
    },
    "PHONE": {
        "pattern": r"\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "severity": "MEDIUM",
    },
    "AADHAAR": {
        "pattern": r"\b[2-9]\d{3}\s\d{4}\s\d{4}\b|\b[2-9]\d{11}\b",
        "severity": "HIGH",
    },
    "SSN": {
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "severity": "HIGH",
    },
    "PASSPORT": {
        "pattern": r"\b[A-Z0-9]{9}\b|\b[A-Z]\d{7}\b",
        "severity": "HIGH",
    },
    "CREDIT_CARD": {
        "pattern": r"\b(?:4\d{3}|5[1-5]\d{2}|6011|3[47]\d{2})[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b|\b3[47]\d{2}[- ]?\d{6}[- ]?\d{5}\b",
        "severity": "HIGH",
    },
    "BANK_ACCOUNT": {
        "pattern": r"\b\d{8,17}\b",
        "severity": "HIGH",
    },
}


class PIIDetector:
    """
    Detector responsible for identifying Personally Identifiable Information (PII)
    within text content using configurable regular expression patterns.
    """

    def __init__(self, custom_patterns: Optional[Dict[str, Dict[str, str]]] = None) -> None:
        """
        Initializes the PIIDetector with default or custom patterns.

        Args:
            custom_patterns: A dictionary mapping PII types (e.g., 'EMAIL') to dictionaries
                             containing 'pattern' (regex string) and optionally 'severity' (str).
        """
        self.patterns: Dict[str, Dict[str, str]] = {}
        for key, val in DEFAULT_PATTERNS.items():
            self.patterns[key] = {
                "pattern": val["pattern"],
                "severity": val["severity"],
            }

        # Override or add custom patterns
        if custom_patterns:
            for key, val in custom_patterns.items():
                if "pattern" in val:
                    self.patterns[key] = {
                        "pattern": val["pattern"],
                        "severity": val.get("severity", "MEDIUM"),
                    }

        # Precompile patterns for runtime efficiency
        self.compiled_patterns = {
            key: re.compile(val["pattern"])
            for key, val in self.patterns.items()
        }

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans input text for matches against compiled PII patterns.
        Resolves overlapping findings by prioritizing longer match spans.

        Args:
            text: The raw text content to analyze.

        Returns:
            A list of dictionary findings, where each finding has:
            - 'type': PII type name (str)
            - 'severity': Severity level (str)
            - 'text': The matched substring (str)
        """
        findings: List[Dict[str, Any]] = []
        if not text:
            return findings

        # Collect all raw matches across all patterns
        raw_findings: List[Dict[str, Any]] = []
        for pii_type, compiled_regex in self.compiled_patterns.items():
            severity = self.patterns[pii_type]["severity"]
            for match in compiled_regex.finditer(text):
                raw_findings.append({
                    "type": pii_type,
                    "severity": severity,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                })

        from shared.utils import remove_overlapping_spans
        findings = remove_overlapping_spans(raw_findings)

        return findings


import os
import re
import yaml
import logging
from typing import Dict, List, Any, Optional
from shared.base_agent import BaseDetector

logger = logging.getLogger(__name__)

# Resolve default regulation rules path relative to this file
DEFAULT_REGULATION_RULES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config",
    "regulation_rules.yaml"
)


class RegulationChecker(BaseDetector):
    """
    Detector responsible for identifying regulatory compliance violations
    (such as GDPR, HIPAA, PCI-DSS, ISO27001, SOC2) within text content
    using configurable regular expressions loaded from a YAML file.
    """

    def __init__(self, rules_path: Optional[str] = None) -> None:
        """
        Initializes the RegulationChecker and loads scanning rules from a YAML file.

        Args:
            rules_path: Absolute or relative path to the regulation rules YAML config.
                        Defaults to the app/config/regulation_rules.yaml file.
        """
        path = rules_path or DEFAULT_REGULATION_RULES_PATH
        self.rules: List[Dict[str, Any]] = []
        self.compiled_rules: List[Dict[str, Any]] = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.rules = data.get("rules", []) if data else []
            logger.info(f"Successfully loaded {len(self.rules)} regulatory rules from {path}")
        except Exception as e:
            logger.error(f"Failed to load regulation rules from {path}: {str(e)}")
            self.rules = []

        # Precompile patterns
        for rule in self.rules:
            regulation = rule.get("regulation")
            severity = rule.get("severity", "Medium")
            description = rule.get("description")
            patterns = rule.get("patterns", [])
            compiled_patterns = []
            for pat in patterns:
                try:
                    compiled_patterns.append(re.compile(pat))
                except re.error as err:
                    logger.error(f"Invalid regex pattern '{pat}' in regulation '{regulation}': {str(err)}")

            if compiled_patterns:
                self.compiled_rules.append({
                    "regulation": regulation,
                    "severity": severity,
                    "description": description,
                    "compiled_patterns": compiled_patterns,
                })

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans input text for regulatory violations.
        Resolves overlapping matches by keeping the longest matched span.

        Args:
            text: The raw text content to check.

        Returns:
            A list of dictionary findings, where each finding has:
            - 'regulation': The regulation standard violated (e.g., GDPR)
            - 'severity': Severity level (str)
            - 'description': Explanation of the violation (str)
        """
        findings: List[Dict[str, Any]] = []
        if not text:
            logger.debug("Empty text provided to RegulationChecker. Returning empty list.")
            return findings

        raw_findings: List[Dict[str, Any]] = []
        for rule in self.compiled_rules:
            regulation = rule["regulation"]
            severity = rule["severity"]
            description = rule["description"]
            for regex in rule["compiled_patterns"]:
                for match in regex.finditer(text):
                    raw_findings.append({
                        "regulation": regulation,
                        "severity": severity,
                        "description": description,
                        "matched": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                    })

        if raw_findings:
            logger.info(f"Found {len(raw_findings)} potential regulatory matches before deduplication.")

        from shared.utils import remove_overlapping_spans
        findings = remove_overlapping_spans(raw_findings)

        if findings:
            logger.warning(f"Detected {len(findings)} regulatory violations.")

        return findings


import os
import re
import yaml
import logging
from typing import Dict, List, Any, Optional
from shared.base_agent import BaseDetector

logger = logging.getLogger(__name__)

# Resolve default rules path relative to this file
DEFAULT_RULES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config",
    "toxicity_rules.yaml"
)


class ToxicityDetector(BaseDetector):
    """
    Detector responsible for identifying toxic text content (Hate Speech, Harassment,
    Violence, Threats, Offensive Language, Discrimination) based on regex rules
    loaded from a YAML configuration file.
    """

    def __init__(self, rules_path: Optional[str] = None) -> None:
        """
        Initializes the ToxicityDetector and loads scanning rules from a YAML file.

        Args:
            rules_path: Absolute or relative path to the toxicity rules YAML config.
                        Defaults to the app/config/toxicity_rules.yaml file.
        """
        path = rules_path or DEFAULT_RULES_PATH
        self.rules: List[Dict[str, Any]] = []
        self.compiled_rules: List[Dict[str, Any]] = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.rules = data.get("rules", []) if data else []
            logger.info(f"Successfully loaded {len(self.rules)} toxicity categories from {path}")
        except Exception as e:
            logger.error(f"Failed to load toxicity rules from {path}: {str(e)}")
            self.rules = []

        # Precompile regexes for each category
        for rule in self.rules:
            category = rule.get("category")
            severity = rule.get("severity", "Medium")
            patterns = rule.get("patterns", [])
            compiled_patterns = []
            for pat in patterns:
                try:
                    compiled_patterns.append(re.compile(pat))
                except re.error as err:
                    logger.error(f"Invalid regex pattern '{pat}' in category '{category}': {str(err)}")

            if compiled_patterns:
                self.compiled_rules.append({
                    "category": category,
                    "severity": severity,
                    "compiled_patterns": compiled_patterns,
                })

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans input text for matches against loaded toxicity rules.
        Resolves overlapping findings by prioritizing longer match spans.

        Args:
            text: The raw text content to analyze.

        Returns:
            A list of dictionary findings, where each finding has:
            - 'category': Toxicity category (str)
            - 'severity': Severity level (str)
            - 'matched': The matched substring (str)
        """
        findings: List[Dict[str, Any]] = []
        if not text:
            logger.debug("Empty text provided to ToxicityDetector. Returning empty list.")
            return findings

        raw_findings: List[Dict[str, Any]] = []
        for rule in self.compiled_rules:
            category = rule["category"]
            severity = rule["severity"]
            for regex in rule["compiled_patterns"]:
                for match in regex.finditer(text):
                    raw_findings.append({
                        "category": category,
                        "severity": severity,
                        "matched": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                    })

        if raw_findings:
            logger.info(f"Found {len(raw_findings)} potential toxicity matches before deduplication.")

        from shared.utils import remove_overlapping_spans
        findings = remove_overlapping_spans(raw_findings)

        if findings:
            logger.warning(f"Detected {len(findings)} toxicity violations.")

        return findings


