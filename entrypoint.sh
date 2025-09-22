#!/usr/bin/env bash
set -euo pipefail

# ---- helpers ---------------------------------------------------------------
retry() {
  local tries="$1"; shift
  local delay="$1"; shift
  local n=1
  until "$@"; do
    if [ $n -ge "$tries" ]; then
      echo "❌ Command failed after $tries attempts: $*"
      return 1
    fi
    echo "⏳ Attempt $n/$tries failed. Retrying in ${delay}s…"
    n=$((n+1))
    sleep "$delay"
  done
}

run_migrations() {
  echo "🔧 Running Alembic migrations (DATABASE_URL detected: ${DATABASE_URL:-unset})"
  # Try up to 20 times with a 3s backoff to cover cold DB / pooled connection warm-up
  retry 20 3 alembic upgrade head
  echo "✅ Migrations up to date."
}

start_worker_bg() {
  echo "🧵 Starting worker in background…"
  # Slow the poll a bit on tiny free instances to be nice to the DB
  export WORKER_POLL_MS="${WORKER_POLL_MS:-3000}"
  python -m app.jobs.worker &
}

start_api_fg() {
  echo "🚀 Starting API…"
  exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
}

# ---- flow ------------------------------------------------------------------
# 1) Migrations first (default ON)
if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  run_migrations
else
  echo "⚠️  RUN_MIGRATIONS=0 -> skipping migrations."
fi

# 2) Worker (default ON) – starts only AFTER migrations succeeded
if [ "${RUN_WORKER:-1}" = "1" ]; then
  start_worker_bg
else
  echo "ℹ️  RUN_WORKER=0 -> worker disabled."
fi

# 3) API in the foreground
start_api_fg
