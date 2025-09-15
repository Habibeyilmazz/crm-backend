#!/bin/sh
set -e

# Required envs: DATABASE_URL, JWT_SECRET (for API)
# Optional: ROLE (api|worker), SUMMARY_ENGINE (rule|t5), WORKER_POLL_MS
: "${ROLE:=api}"

if [ "$ROLE" = "worker" ]; then
  echo "[container] Starting WORKER"
  exec python -m app.jobs.worker
else
  echo "[container] Starting API"
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
