# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from passlib.hash import bcrypt
from jose import jwt
from typing import List
from sqlalchemy.orm import Session
from . import schemas, models
from .deps import get_db, current_user_dep
from .models import Note, Job
import os

app = FastAPI(title="Mini CRM")

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
ALGO = "HS256"

@app.get("/health")
def health(): return {"ok": True}

# --- AUTH ---
@app.post("/auth/signup")
def signup(payload: schemas.SignupIn, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=payload.email).first():
        raise HTTPException(status_code=400, detail="Email already used")
    user = models.User(email=payload.email,
                       password_hash=bcrypt.hash(payload.password),
                       role="AGENT")
    db.add(user); db.commit(); db.refresh(user)
    return {"id": user.id, "email": user.email}

@app.post("/auth/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=payload.email).first()
    if not user or not bcrypt.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Bad credentials")
    token = jwt.encode({"sub": str(user.id), "role": user.role}, JWT_SECRET, algorithm=ALGO)
    return {"access_token": token}

# --- NOTES (minimal) ---
@app.post("/notes", response_model=schemas.NoteOut)
def create_note(body: schemas.NoteCreateIn,
                db: Session = Depends(get_db),
                me=Depends(current_user_dep)):
    note = models.Note(user_id=me.id, raw_text=body.raw_text, status="queued")
    db.add(note); db.commit(); db.refresh(note)

    job = models.Job(note_id=note.id, kind="summarize", status="queued")
    db.add(job); db.commit()

    return note

@app.get("/notes/{note_id}", response_model=schemas.NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db), me=Depends(current_user_dep)):
    note = db.get(models.Note, note_id)
    if not note: raise HTTPException(status_code=404, detail="Not found")
    if me.role != "ADMIN" and note.user_id != me.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return note

@app.get("/notes", response_model=List[schemas.NoteOut])
def list_notes(limit: int = 50, offset: int = 0,
               db: Session = Depends(get_db),
               me=Depends(current_user_dep)):
    q = db.query(models.Note)
    if me.role != "ADMIN":
        q = q.filter(models.Note.user_id == me.id)
    return q.order_by(models.Note.created_at.desc()).offset(offset).limit(limit).all()