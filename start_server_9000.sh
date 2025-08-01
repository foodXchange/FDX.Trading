#!/bin/bash

echo "========================================"
echo "Starting FoodXchange Dev Server (Port 9000)"
echo "========================================"

# Set environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export PORT=9000
export PYTHONPATH=/workspace

echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"

# Check if we're in the dev container
if [ -f /.dockerenv ]; then
    echo "✅ Running in Docker container"
else
    echo "⚠️  Not running in Docker container"
fi

# Check if dependencies are installed
if python -c "import uvicorn" 2>/dev/null; then
    echo "✅ uvicorn is installed"
else
    echo "❌ uvicorn not found. Installing..."
    pip install uvicorn[standard]
fi

echo "Starting FastAPI server on port 9000 with auto-reload..."
echo "Server will be available at: http://localhost:9000"
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload --log-level info 