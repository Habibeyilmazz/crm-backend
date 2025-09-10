from fastapi import FastAPI
from .db import Base, engine

# Create tables directly (for dev). In prod, use Alembic migrations
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
