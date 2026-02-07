#!/bin/bash
set -e

cd /app

# Run database migrations
echo "Running SSO database migrations..."
alembic upgrade head

# Start the application
exec gunicorn source:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
