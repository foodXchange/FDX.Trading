#\!/bin/bash
echo "Starting FoodXchange Flask App..."

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
fi

# Get port from environment
PORT=${PORT:-8000}
echo "Starting app on port $PORT"

# Start the Flask app with gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --timeout 600 --workers 1 --worker-class sync app:app
