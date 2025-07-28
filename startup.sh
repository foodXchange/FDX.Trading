#!/bin/bash
echo "Starting FoodXchange minimal app..."
python -m uvicorn minimal_app:app --host 0.0.0.0 --port $PORT
