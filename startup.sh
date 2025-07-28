#!/bin/bash
echo "Starting FoodXchange Flask app..."
gunicorn --bind 0.0.0.0:$PORT --timeout 600 app:app