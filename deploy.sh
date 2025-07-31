#!/bin/bash
# FoodXchange Deployment Script

set -e

echo "🚀 Starting FoodXchange deployment..."

# Check if running in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "📦 Production deployment detected"
    
    # Install production dependencies
    pip install -r foodxchange/requirements.txt --no-dev
    
    # Set production environment
    export DEBUG=false
    export LOG_LEVEL=INFO
    
else
    echo "🔧 Development deployment detected"
    
    # Install all dependencies
    pip install -r foodxchange/requirements.txt
    pip install -r requirements-dev.txt
fi

# Run database migrations
echo "🗄️ Running database migrations..."
python -m alembic upgrade head

# Start the application
echo "🌐 Starting FoodXchange server..."
python start_server_fixed.py
