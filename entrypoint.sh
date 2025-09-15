#!/usr/bin/env bash
set -e

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  echo "Running Alembic migrations…"
  alembic upgrade head
fi

if [ "${RUN_MODE:-api}" = "worker" ]; then
  echo "Starting worker…"
  python -m app.jobs.worker
else
  echo "Starting API…"
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
