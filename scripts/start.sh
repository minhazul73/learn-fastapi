#!/usr/bin/env bash
# scripts/start.sh – Production entrypoint
# Called by Dockerfile CMD or manually on the server.
set -e

echo "==> Running database migrations..."
alembic upgrade head

echo "==> Starting application..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "${WORKERS:-1}" \
    --bind "0.0.0.0:${PORT:-8000}" \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile -
