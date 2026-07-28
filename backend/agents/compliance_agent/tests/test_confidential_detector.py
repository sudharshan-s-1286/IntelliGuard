import pytest
from agents.compliance_agent.detector import ConfidentialDetector


@pytest.fixture
def detector() -> ConfidentialDetector:
    return ConfidentialDetector()


def test_detect_aws_key(detector: ConfidentialDetector) -> None:
    text = "AWS Key ID is AKIAFAKE123456789012 and another key is ASIAFAKE123456789012."
    findings = detector.detect(text)
    
    aws_keys = [f for f in findings if f["type"] == "AWS_ACCESS_KEY"]
    assert len(aws_keys) == 2
    assert any(k["text"] == "AKIAFAKE123456789012" for k in aws_keys)
    assert any(k["text"] == "ASIAFAKE123456789012" for k in aws_keys)
    assert all(k["severity"] == "CRITICAL" for k in aws_keys)


def test_detect_jwt_token(detector: ConfidentialDetector) -> None:
    text = "Authorization token: eyJhbGciOiJIUzI1NiJ9.fake.payload.FAKE"
    findings = detector.detect(text)
    
    jwts = [f for f in findings if f["type"] == "JWT_TOKEN"]
    assert len(jwts) == 1
    assert jwts[0]["text"].startswith("eyJ")


def test_detect_bearer_token(detector: ConfidentialDetector) -> None:
    text = "The request header contains: Bearer FAKE_ACCESS_TOKEN123"
    findings = detector.detect(text)
    
    bearers = [f for f in findings if f["type"] == "BEARER_TOKEN"]
    assert len(bearers) == 1
    assert bearers[0]["text"] == "Bearer FAKE_ACCESS_TOKEN123"


def test_detect_api_key(detector: ConfidentialDetector) -> None:
    text = "stripe: apikey: TEST_STRIPE_SECRET_KEY or apikey: my-secret-api-key-99."
    findings = detector.detect(text)
    
    keys = [f for f in findings if f["type"] == "API_KEY"]
    assert len(keys) == 2
    assert any("TEST_STRIPE_SECRET_KEY" in k["text"] for k in keys)
    assert any("apikey: my-secret-api-key-99" in k["text"] for k in keys)


def test_detect_ssh_key(detector: ConfidentialDetector) -> None:
    text = """
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEA0Yg9N/F...
    -----END RSA PRIVATE KEY-----
    """
    findings = detector.detect(text)
    
    ssh_keys = [f for f in findings if f["type"] == "SSH_KEY"]
    assert len(ssh_keys) == 1
    assert "BEGIN RSA PRIVATE KEY" in ssh_keys[0]["text"]


def test_detect_password(detector: ConfidentialDetector) -> None:
    text = "database_password = FAKE_PASSWORD123! or pwd: testuserpass"
    findings = detector.detect(text)
    
    passwords = [f for f in findings if f["type"] == "PASSWORD"]
    assert len(passwords) == 1
    assert passwords[0]["text"] == "pwd: testuserpass"


def test_detect_secret(detector: ConfidentialDetector) -> None:
    text = "client_secret = SuperSecretString999"
    findings = detector.detect(text)
    
    secrets = [f for f in findings if f["type"] == "SECRET"]
    assert len(secrets) == 1
    assert secrets[0]["text"] == "client_secret = SuperSecretString999"


def test_detect_db_connection(detector: ConfidentialDetector) -> None:
    text = "postgres://username:pwd123@localhost:5432/mydb_name"
    findings = detector.detect(text)
    
    dbs = [f for f in findings if f["type"] == "DB_CONNECTION_STRING"]
    assert len(dbs) == 1
    assert dbs[0]["text"] == "postgres://username:pwd123@localhost:5432/mydb_name"


def test_overlap_deduplication(detector: ConfidentialDetector) -> None:
    # A database connection string matches db connection string, but contains a password portion
    # like pwd123. The overlap resolution should flag the connection string as a single
    # critical finding instead of separate PASSWORD and DB_CONNECTION_STRING matches.
    text = "db: postgres://username:pwd123@localhost:5432/mydb_name"
    findings = detector.detect(text)
    
    db_findings = [f for f in findings if f["type"] == "DB_CONNECTION_STRING"]
    password_findings = [f for f in findings if f["type"] == "PASSWORD"]
    
    assert len(db_findings) == 1
    assert len(password_findings) == 0


def test_custom_patterns() -> None:
    custom = {
        "DOCKER_TOKEN": {
            "pattern": r"\bdckt_[a-zA-Z0-9]{32}\b",
            "severity": "CRITICAL"
        }
    }
    custom_detector = ConfidentialDetector(custom_patterns=custom)
    text = "Here is the token: dckt_abc123xyz78901234567890123456789"
    findings = custom_detector.detect(text)
    
    tokens = [f for f in findings if f["type"] == "DOCKER_TOKEN"]
    assert len(tokens) == 1
    assert tokens[0]["text"] == "dckt_abc123xyz78901234567890123456789"


def test_no_secrets(detector: ConfidentialDetector) -> None:
    text = "Nothing sensitive to see here. Move along."
    findings = detector.detect(text)
    assert len(findings) == 0


def test_empty_string(detector: ConfidentialDetector) -> None:
    findings = detector.detect("")
    assert len(findings) == 0
