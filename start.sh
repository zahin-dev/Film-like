#!/usr/bin/env bash
# Start the Film-like development servers

# Stop the script if a command fails
set -e

echo "=== Starting Film-like ==="

# Check that the virtual environment exists
if [ ! -f "backend/venv/bin/activate" ]; then
    echo "Error: virtual environment not found."
    echo "Run this command first to initialize the project:"
    echo "    ./setup.sh"
    exit 1
fi

# Check that node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Error: frontend dependencies not found."
    echo "Run this command first to initialize the project."
    echo "    ./setup.sh"
    exit 1
fi

# Start PostgreSQL via Docker (safe to call if already running)
echo "Starting PostgreSQL..."
docker compose up -d
echo "PostgreSQL ready."

# Start the backend in the background
echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!
cd ..

# Start the frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== Film-like is running ==="
echo "  Frontend : http://localhost:5173"
echo "  Backend  : http://localhost:8000"
echo "  Swagger  : http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait and handle Ctrl+C cleanly
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped.'" EXIT
wait
