# Tool-51 — Data Retention and Disposal Manager

A full-stack AI-powered web application for managing data retention policies and disposal workflows.

## Architecture

```
Frontend (React + Vite) :80
         |
         v
Backend (Spring Boot) :8080
         |
    _____|_____
   |           |
PostgreSQL   Redis
  :5432       :6379
         |
         v
 AI Service (Flask) :5000
         |
         v
  Groq API (LLaMA)
```

## Prerequisites

- Docker Desktop
- Docker Compose
- Git

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/tecsxpert/data-retention-disposal-manager
   cd data-retention-disposal-manager
   ```

2. Copy `.env.example` and fill in your values:
   ```bash
   cp .env.example .env
   ```

3. Start all services:
   ```bash
   docker-compose up --build
   ```

4. Access:
   - Frontend: http://localhost
   - Backend API / Swagger: http://localhost:8080/swagger-ui.html
   - AI Service health: http://localhost:5000/health

## Default Login

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| User  | user1    | user123   |

## Environment Variables

| Variable        | Description               | Default                        |
|-----------------|---------------------------|--------------------------------|
| DB_HOST         | PostgreSQL host            | localhost                      |
| DB_NAME         | Database name              | retentiondb                    |
| DB_USER         | Database user              | postgres                       |
| DB_PASS         | Database password          | —                              |
| REDIS_HOST      | Redis host                 | localhost                      |
| JWT_SECRET      | JWT signing secret (≥32 chars) | —                         |
| MAIL_USERNAME   | Gmail address              | —                              |
| MAIL_PASSWORD   | Gmail app password         | —                              |
| GROQ_API_KEY    | Groq AI API key            | — (AI analysis disabled if empty) |

## Features

- **Records management** — create, edit, soft-delete, and permanently delete data records
- **Search & pagination** — keyword search across name and description
- **Dashboard stats** — real-time counts of total, active, expiring, and disposed records
- **AI analysis** — per-record LLaMA-powered compliance summary and risk score via Groq
- **Expiry scheduler** — daily job marks ACTIVE records expiring within 30 days as EXPIRING and sends email reminders
- **CSV export** — download all records as a spreadsheet
- **Audit trail** — every create/update/delete action is logged with the performing user
- **JWT auth** — stateless authentication with role-based access (USER / ADMIN)
- **Redis caching** — 10-minute TTL on record lists and stats

## Tech Stack

| Layer      | Technology                            |
|------------|---------------------------------------|
| Backend    | Java 17, Spring Boot 3.2, Spring Security |
| Database   | PostgreSQL 15 (Flyway migrations)     |
| Cache      | Redis 7                               |
| AI Service | Python 3.11, Flask 3, Groq SDK        |
| Frontend   | React 18, Vite 5, React Router v6     |
| Infra      | Docker, Docker Compose                |

## API Endpoints

| Method | Path                        | Auth  | Description                        |
|--------|-----------------------------|-------|------------------------------------|
| POST   | /api/auth/register          | open  | Register a new user                |
| POST   | /api/auth/login             | open  | Login and receive JWT              |
| GET    | /api/records                | JWT   | List all records (paginated)       |
| POST   | /api/records                | JWT   | Create a record                    |
| GET    | /api/records/{id}           | JWT   | Get record by ID                   |
| PUT    | /api/records/{id}           | JWT   | Update a record                    |
| DELETE | /api/records/{id}           | JWT   | Soft-delete (dispose) a record     |
| DELETE | /api/records/{id}/permanent | ADMIN | Permanently delete a record        |
| POST   | /api/records/{id}/analyze   | JWT   | Run AI analysis and store result   |
| GET    | /api/records/search?q=      | JWT   | Search records                     |
| GET    | /api/records/stats          | JWT   | Dashboard statistics               |
| GET    | /api/records/export         | JWT   | Download records as CSV            |

Full interactive docs available at `http://localhost:8080/swagger-ui.html` when running.

## Running Tests

```bash
cd backend/tool
./mvnw test
```
