# Mini CRM Backend

A learning project to practice backend development, deployment, and database management.  
Built with **FastAPI**, **PostgreSQL**, **Alembic**, and **Docker**. Deployed on **Koyeb** with a Neon database.

## Features
- User authentication with JWT
- CRUD operations for Notes (create, list, update, delete)
- Swagger UI at `/docs` for easy API exploration
- Alembic migrations for schema management
- Dockerized setup for local development and cloud deployment

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (Neon Cloud)
- **Auth:** JWT
- **Migrations:** Alembic
- **Containerization:** Docker
- **Deployment:** Koyeb

## Getting Started

### Run locally
```bash
git clone https://github.com/Habibeyilmazz/crm-backend.git
cd crm-backend
pip install -r requirements.txt
uvicorn app.main:app --reload

Run with docker
```bash
docker build -t crm-backend .
docker run -p 8000:8000 crm-backend

Example API Calls:
POST /auth/signup – Register a new user
POST /auth/login – Login and receive JWT
POST /notes – Create a note (requires JWT)
GET /notes – List all notes for the user

Deployment
Hosted on Koyeb
Database on Neon