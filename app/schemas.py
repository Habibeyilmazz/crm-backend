# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class NoteCreateIn(BaseModel):
    raw_text: str

class NoteOut(BaseModel):
    id: int
    raw_text: str
    summary: Optional[str] = None
    status: str
    class Config:
        from_attributes = True
