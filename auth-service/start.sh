#!/bin/bash

echo "Waiting for PostgreSQL..."
sleep 10

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8001