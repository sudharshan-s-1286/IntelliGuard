"""Constants for the Privacy Agent."""

from __future__ import annotations

PII_TYPE_EMAIL: str = "email"
PII_TYPE_PHONE: str = "phone"
PII_TYPE_SSN: str = "ssn"
PII_TYPE_CREDIT_CARD: str = "credit_card"
PII_TYPE_IP_ADDRESS: str = "ip_address"
PII_TYPE_NAME: str = "name"
PII_TYPE_ADDRESS: str = "address"
PII_TYPE_DATE_OF_BIRTH: str = "date_of_birth"
PII_TYPE_PASSPORT: str = "passport"
PII_TYPE_DRIVER_LICENSE: str = "driver_license"
PII_TYPE_MEDICAL_RECORD: str = "medical_record"
PII_TYPE_FINANCIAL_ACCOUNT: str = "financial_account"

ALL_PII_TYPES: frozenset[str] = frozenset(
    {
        PII_TYPE_EMAIL,
        PII_TYPE_PHONE,
        PII_TYPE_SSN,
        PII_TYPE_CREDIT_CARD,
        PII_TYPE_IP_ADDRESS,
        PII_TYPE_NAME,
        PII_TYPE_ADDRESS,
        PII_TYPE_DATE_OF_BIRTH,
        PII_TYPE_PASSPORT,
        PII_TYPE_DRIVER_LICENSE,
        PII_TYPE_MEDICAL_RECORD,
        PII_TYPE_FINANCIAL_ACCOUNT,
    }
)

PII_LABEL_MAP: dict[str, str] = {
    PII_TYPE_EMAIL: "Email Address",
    PII_TYPE_PHONE: "Phone Number",
    PII_TYPE_SSN: "Social Security Number",
    PII_TYPE_CREDIT_CARD: "Credit Card Number",
    PII_TYPE_IP_ADDRESS: "IP Address",
    PII_TYPE_NAME: "Person Name",
    PII_TYPE_ADDRESS: "Physical Address",
    PII_TYPE_DATE_OF_BIRTH: "Date of Birth",
    PII_TYPE_PASSPORT: "Passport Number",
    PII_TYPE_DRIVER_LICENSE: "Driver License Number",
    PII_TYPE_MEDICAL_RECORD: "Medical Record",
    PII_TYPE_FINANCIAL_ACCOUNT: "Financial Account",
}

SENSITIVITY_HIGH: str = "high"
SENSITIVITY_MEDIUM: str = "medium"
SENSITIVITY_LOW: str = "low"

SENSITIVITY_WEIGHTS: dict[str, float] = {
    SENSITIVITY_HIGH: 1.0,
    SENSITIVITY_MEDIUM: 0.6,
    SENSITIVITY_LOW: 0.2,
}

PII_SENSITIVITY: dict[str, str] = {
    PII_TYPE_SSN: SENSITIVITY_HIGH,
    PII_TYPE_CREDIT_CARD: SENSITIVITY_HIGH,
    PII_TYPE_PASSPORT: SENSITIVITY_HIGH,
    PII_TYPE_DRIVER_LICENSE: SENSITIVITY_HIGH,
    PII_TYPE_MEDICAL_RECORD: SENSITIVITY_HIGH,
    PII_TYPE_FINANCIAL_ACCOUNT: SENSITIVITY_HIGH,
    PII_TYPE_EMAIL: SENSITIVITY_MEDIUM,
    PII_TYPE_PHONE: SENSITIVITY_MEDIUM,
    PII_TYPE_IP_ADDRESS: SENSITIVITY_MEDIUM,
    PII_TYPE_NAME: SENSITIVITY_LOW,
    PII_TYPE_ADDRESS: SENSITIVITY_LOW,
    PII_TYPE_DATE_OF_BIRTH: SENSITIVITY_LOW,
}

MASK_CHAR: str = "*"
DEFAULT_MASK_PATTERN: str = "***"

LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%dT%H:%M:%S%z"

DEFAULT_MAX_ENTITIES_PER_SCAN: int = 1000
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5
DEFAULT_RISK_SCORE_CAP: float = 100.0

DEFAULT_SCAN_ID_PREFIX: str = "privacy_scan"
