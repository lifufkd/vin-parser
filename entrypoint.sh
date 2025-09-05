#!/bin/sh

echo "Starting server..."
uvicorn src.main:app --host 0.0.0.0 --port 8000
