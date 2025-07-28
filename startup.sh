#!/bin/bash

# Azure App Service startup script
echo "Starting FoodXchange application..."

# Install dependencies if needed
if [ -f requirements.txt ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the application using Python module execution
echo "Starting FastAPI application..."
python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port $PORT