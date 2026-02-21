#!/bin/bash
# run_init_tests.sh: Test runner for GABBE scripts/init.py

echo "Starting tests for scripts/init.py..."

# Ensure we're running from the project root
cd "$(dirname "$0")/../.." || exit 1

# Activate local virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Please create one with 'python3 -m venv .venv'"
    exit 1
fi

# Install pytest if it's somehow missing in the env
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Attempting to install pytest..."
    pip install pytest
fi

# Run pytest specifically for the init.py test suite
echo "Running pytest scripts/tests/test_init.py -v"
pytest scripts/tests/test_init.py -v

if [ $? -eq 0 ]; then
    echo "All tests passed successfully! ✅"
else
    echo "Some tests failed. ❌ Please check the output above."
    exit 1
fi
