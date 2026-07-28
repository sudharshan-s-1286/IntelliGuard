#!/bin/bash
echo "======================================"
echo " IntelliGuard CI/CD Test Suite Runner "
echo "======================================"

source venv/bin/activate

echo ""
echo "[1] Running Pytest Suite with Coverage..."
echo "--------------------------------------"
python3 -m pytest tests/ --cov=agents.security_agent --cov-report=term-missing > test_report.txt

echo ""
echo "[2] Running Performance Benchmark..."
echo "--------------------------------------"
python3 tests/performance/benchmark.py >> test_report.txt

echo ""
echo "Test execution complete! Review test_report.txt for details."
cat test_report.txt
