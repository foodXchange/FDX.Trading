#!/bin/bash

# Azure App Service startup script - Simple version
echo "Starting FoodXchange application..."

# Activate the virtual environment created by Oryx
if [ -d "/home/site/wwwroot/antenv" ]; then
    echo "Activating virtual environment..."
    source /home/site/wwwroot/antenv/bin/activate
else
    echo "WARNING: Virtual environment not found at /home/site/wwwroot/antenv"
fi

# Display Python and pip information for debugging
echo "Python version:"
python --version
echo "Python path:"
which python
echo "Pip packages location:"
pip show fastapi | grep Location || echo "FastAPI not found"

# Set the port
export PORT=${PORT:-8000}
echo "Using port: $PORT"

# Try to start the minimal app first
echo "Starting minimal FastAPI application..."
cd /home/site/wwwroot
python -m uvicorn minimal_app:app --host 0.0.0.0 --port $PORT