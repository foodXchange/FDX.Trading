#!/bin/bash

# Azure App Service Startup Script

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=8000
fi

echo "Starting FoodXchange on port $PORT..."

# Create database file if using SQLite
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="sqlite:///./foodxchange.db"
    echo "Using SQLite database"
fi

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT