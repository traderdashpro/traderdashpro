#!/bin/bash

# Startup script for Render
# This ensures migrations run before the app starts

echo "Starting Trading Insights Backend..."

# Set Flask app
export FLASK_APP=app.py

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start the application
echo "Starting Flask application..."
exec python app.py 