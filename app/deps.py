# deps.py
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import User
import os

JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
ALGO = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGO])
        user_id: int = int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# convenience dependency for FastAPI
from fastapi.security import HTTPBearer
bearer = HTTPBearer()

def current_user_dep(credentials=Depends(bearer), db: Session = Depends(get_db)):
    return get_current_user(credentials.credentials, db)
