#!/bin/bash

# Deployment script for Render
# This script will be run during the build process

echo "Starting deployment..."

# Set Flask app
export FLASK_APP=app.py

# Wait for database to be ready (if needed)
echo "Waiting for database connection..."
sleep 5

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start the application
echo "Starting Flask application..."
python app.py 