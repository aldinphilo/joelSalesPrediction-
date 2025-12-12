#!/bin/sh
set -e

# Attempt to download the Model directory if not present
echo "Checking for /app/Model..."
python /app/scripts/download_model.py || true

# Start the application
echo "Starting application..."
exec python /app/app.py
