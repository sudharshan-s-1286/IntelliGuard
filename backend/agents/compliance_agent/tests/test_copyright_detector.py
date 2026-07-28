import pytest
from agents.compliance_agent.detector import CopyrightDetector

@pytest.fixture
def detector():
    return CopyrightDetector()

def test_detect_copyright_warning(detector):
    text = "This file is Copyright (c) 2023 by ACME Corp. All rights reserved."
    findings = detector.detect(text)
    assert len(findings) >= 1
    assert any(f["issue"] == "Possible copyrighted content" for f in findings)
    assert any(f["severity"] == "Low" for f in findings)
    assert any("Copyright" in f["details"] or "warning" in f["details"].lower() for f in findings)

def test_detect_license_sensitive_code(detector):
    text = "This software is licensed under the GNU General Public License."
    findings = detector.detect(text)
    assert len(findings) == 1
    assert findings[0]["issue"] == "Possible copyrighted content"
    assert findings[0]["details"] == "License-sensitive code"

def test_detect_large_copied_passages_quotes(detector):
    long_string = '"' + "A" * 250 + '"'
    text = f"Here is a quote: {long_string}"
    findings = detector.detect(text)
    assert len(findings) == 1
    assert findings[0]["issue"] == "Possible copyrighted content"
    assert findings[0]["details"] == "Large copied passages"

def test_detect_large_copied_passages_markdown(detector):
    text = "> line 1\n> line 2\n> line 3\n> line 4\nSome other text."
    findings = detector.detect(text)
    assert len(findings) == 1
    assert findings[0]["issue"] == "Possible copyrighted content"
    assert findings[0]["details"] == "Large copied passages"

def test_detect_excessive_quotations(detector):
    text = "He said 'hello'. She said 'world'. Then 'foo' and 'bar' and 'baz' and 'qux'."
    findings = detector.detect(text)
    assert len(findings) >= 1
    assert any(f["details"] == "Excessive quotations" for f in findings)

def test_no_findings(detector):
    text = "This is a clean file with original content written by the author."
    findings = detector.detect(text)
    assert len(findings) == 0

def test_overlapping_matches_resolved(detector):
    text = "Copyright (c) 2023 GNU General Public License"
    findings = detector.detect(text)
    # Both might match depending on boundaries, ensure no exceptions and structure is maintained
    assert len(findings) >= 1
    assert all(f["issue"] == "Possible copyrighted content" for f in findings)
