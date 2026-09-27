# AURA — Autonomous Unified Reasoning Agent

A runnable, extensible final-year project starter. It includes a FastAPI backend, Next.js chat UI, PostgreSQL, a task planner, a permission-aware tool registry, CSV analysis, document retrieval, task verification, and Docker Compose.

## Quick start (Docker)

1. Copy `.env.example` to `.env` and set a long `JWT_SECRET`.
2. Run `docker compose up --build`.
3. Open the frontend at http://localhost:3000 and API docs at http://localhost:8000/docs.

The backend has a local rule-based planner so the app runs without an LLM key. Configure `OPENAI_API_KEY` to enable model-backed responses. External research is intentionally unavailable until a real search provider is configured.

## Local backend

Use Python 3.11+. Install `backend/requirements.txt`, set `DATABASE_URL` (SQLite is supported for local development), then run `uvicorn app.main:app --reload` from `backend/`. Run the frontend from `frontend/` with `npm install` and `npm run dev`.

## Project map

See [ARCHITECTURE.md](docs/ARCHITECTURE.md), [API.md](docs/API.md), [DATABASE.md](docs/DATABASE.md), [SECURITY.md](docs/SECURITY.md), [TESTING.md](docs/TESTING.md), and [DEPLOYMENT.md](docs/DEPLOYMENT.md).

This is a student project foundation, not a production security certification. Code execution, outbound search, and high-risk actions are not enabled by default.
