#!/usr/bin/env bash
# Clean up generated files and caches from the Film-like project

HARD=false
if [ "$1" == "--hard" ]; then
    HARD=true
fi

echo "=== Film-like Clean ==="

# 1. Python caches
echo "Cleaning Python caches..."
find . -type d -name "__pycache__" -not -path '*/venv/*' -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -not -path '*/venv/*' -delete 2>/dev/null || true
find . -name "*.pyo" -not -path '*/venv/*' -delete 2>/dev/null || true

# 2. pytest cache and coverage
echo "Cleaning test artifacts..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
find . -name ".coverage" -delete 2>/dev/null || true

# 3. Vite build artifacts
echo "Cleaning frontend build artifacts..."
rm -rf frontend/dist 2>/dev/null || true
rm -rf frontend/dist-ssr 2>/dev/null || true

# 4. OS files
echo "Cleaning OS artifacts..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# 5. Hard mode - reset everything reinstallable
if [ "$HARD" = true ]; then
    echo ""
    echo "WARNING: Hard mode will delete node_modules, venv, and .env files."
    read -p "Are you sure? This cannot be undone. (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi

    echo "Hard cleaning..."

    # Remove Python virtual environment
    rm -rf backend/venv 2>/dev/null || true
    echo "  backend/venv deleted"

    # Remove node_modules
    rm -rf frontend/node_modules 2>/dev/null || true
    echo "  frontend/node_modules deleted"

    # Remove .env files
    rm -f backend/.env 2>/dev/null || true
    rm -f frontend/.env 2>/dev/null || true
    echo "  .env files deleted"

    echo ""
    echo "Hard clean complete. Run ./setup.sh to reinitialize the project."
else
    echo ""
    echo "=== Clean complete ==="
    echo "Tip: run './clean.sh --hard' for a full reset (deletes venv, node_modules, .env files)"
fi
