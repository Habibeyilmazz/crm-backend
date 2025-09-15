# app/jobs/worker.py
import os, time
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Job, Note
from ..summarizer.rule_summarizer import summarize_rule_based

# optional tiny LLM
USE_T5 = os.getenv("SUMMARY_ENGINE", "rule").lower() == "t5"
if USE_T5:
    from ..summarizer.t5_summarizer import summarize_t5

POLL_MS = int(os.getenv("WORKER_POLL_MS", "500"))

def backoff_seconds(attempts: int) -> int:
    # 1m, 2m, 4m, ... capped 15m
    return min(60 * (2 ** max(0, attempts - 1)), 900)

def fetch_next_job(db: Session):
    row = db.execute(text("""
        SELECT id FROM jobs
        WHERE status='queued' AND next_run_at <= NOW()
        ORDER BY created_at
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    """)).first()
    return row[0] if row else None

def summarize(text_in: str) -> str:
    if USE_T5:
        return summarize_t5(text_in)
    return summarize_rule_based(text_in)

def run_once() -> bool:
    db = SessionLocal()
    try:
        db.begin()
        job_id = fetch_next_job(db)
        if not job_id:
            db.rollback()
            return False

        job = db.get(Job, job_id)
        job.status = "processing"
        job.updated_at = datetime.utcnow()
        db.commit()  # release lock quickly

        try:
            note = db.get(Note, job.note_id)
            if not note:
                raise RuntimeError("Note not found")

            summary = summarize(note.raw_text)
            note.summary = summary
            note.status = "done"
            job.status = "done"
            job.updated_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            db.rollback()
            db.begin()
            job = db.get(Job, job_id)
            job.attempts += 1
            job.last_error = str(e)
            if job.attempts >= job.max_attempts:
                job.status = "failed"
                note = db.get(Note, job.note_id)
                if note: note.status = "failed"
            else:
                job.status = "queued"
                job.next_run_at = datetime.utcnow() + timedelta(seconds=backoff_seconds(job.attempts))
            job.updated_at = datetime.utcnow()
            db.commit()
        return True
    finally:
        db.close()

def main():
    print("Worker started. Engine:", "t5-small" if USE_T5 else "rule-based")
    while True:
        worked = run_once()
        if not worked:
            time.sleep(POLL_MS / 1000)

if __name__ == "__main__":
    main()
