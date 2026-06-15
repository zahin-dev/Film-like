#!/usr/bin/env bash
# Run the Film-like backend test suite with coverage

# Stop the script if a command fails
set -e

echo "=== Film-like Tests ==="

# Check that the virtual environment exists
if [ ! -f "backend/venv/bin/activate" ]; then
    echo "Error: virtual environment not found."
    echo "Run this command first to initialize the project:"
    echo "    ./setup.sh"
    exit 1
fi

# Run pytest with coverage from the backend directory
echo "Running tests..."
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app --cov-report=term-missing
