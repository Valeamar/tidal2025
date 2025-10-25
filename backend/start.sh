#!/bin/bash
# Startup script for Farmer Budget Optimizer

set -e

# Default values
ENVIRONMENT=${ENVIRONMENT:-development}
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}

echo "Starting Farmer Budget Optimizer API..."
echo "Environment: $ENVIRONMENT"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p logs data cache backups

# Set environment file
if [ -f ".env.$ENVIRONMENT" ]; then
    echo "Using environment file: .env.$ENVIRONMENT"
    cp ".env.$ENVIRONMENT" .env
fi

# Start the application
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting in development mode with auto-reload..."
    uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
elif [ "$ENVIRONMENT" = "production" ]; then
    echo "Starting in production mode..."
    uvicorn app.main:app --host "$HOST" --port "$PORT" --workers "$WORKERS"
else
    echo "Starting in $ENVIRONMENT mode..."
    uvicorn app.main:app --host "$HOST" --port "$PORT" --workers 2
fi