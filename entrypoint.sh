#!/usr/bin/env bash
set -e

  alembic upgrade head

if [ "$APP_MODE" = "worker" ]; then
  python -m app.jobs.worker
else
  uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
fi