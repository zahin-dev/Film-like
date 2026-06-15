#!/usr/bin/env bash
# One-time setup script for Film-like development environment

# Stop the script if a command fails
set -e

echo "=== Film-like Setup ==="

# 1. Check for Python 3.11+
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing..."
    sudo apt update && sudo apt install python3 python3-venv python3-pip -y
fi

PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    echo "Python 3.11+ required. Found $PYTHON_MAJOR.$PYTHON_MINOR"
    exit 1
fi

# 2. Check for Node.js 18+
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -e 'process.stdout.write(String(process.versions.node.split(".")[0]))')
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Node.js 18+ required. Found $NODE_VERSION"
    exit 1
fi

# 3. Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found."
    echo ""
    echo "On Ubuntu, install Docker Engine and Docker Compose with:"
    echo "    sudo apt update"
    echo "    sudo apt install ca-certificates curl -y"
    echo "    curl -fsSL https://get.docker.com | sudo sh"
    echo "    sudo usermod -aG docker \$USER"
    echo ""
    echo "Then log out and log back in, or restart your terminal session."
    echo "After that, run ./setup.sh again."
    echo ""
    echo "Official docs: https://docs.docker.com/engine/install/ubuntu/"
    exit 1
fi

# 4. Check for Docker Compose v2
if ! docker compose version &> /dev/null; then
    echo "Docker Compose v2 plugin not found."
    echo ""
    echo "On Ubuntu, install it with:"
    echo "    sudo apt update"
    echo "    sudo apt install docker-compose-plugin -y"
    echo ""
    echo "Then check with:"
    echo "    docker compose version"
    echo ""
    echo "Official docs: https://docs.docker.com/compose/install/linux/"
    exit 1
fi

# 5. Setup backend
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Backend ready."
cd ..

# 6. Create backend .env
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/your_jwt_secret_key/$SECRET_KEY/" backend/.env
    echo "backend/.env created with a generated SECRET_KEY"
else
    echo "backend/.env already exists - skipping"
fi

# 7. Setup frontend
echo "Setting up frontend..."
cd frontend
npm install
echo "Frontend ready."
cd ..

# 8. Create frontend .env
if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "frontend/.env created"
else
    echo "frontend/.env already exists - skipping"
fi

# 9. Start PostgreSQL via Docker
echo "Starting PostgreSQL..."
docker compose up -d

echo "Waiting for PostgreSQL to be ready..."
until docker exec cinemood_db pg_isready -U cinemood -d cinemood > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL running on port 5432."

# 10. Run database migrations
echo "Running database migrations..."
cd backend
source venv/bin/activate
alembic upgrade head
echo "Migrations applied."

# 11. Seed reference data (tags)
echo "Seeding tags..."
python seeds/seed_tag.py
echo "Tags seeded."
cd ..

echo ""
echo "=== Setup complete ==="
echo "To activate your virtual environment:"
echo "    source backend/venv/bin/activate"
echo "To start the app:"
echo "    ./start.sh"
