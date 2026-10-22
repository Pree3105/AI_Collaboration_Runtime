# AI Collaboration Runtime - Quick Start

Captures engineering workflows as Execution Graphs (DAGs), stores them persistently, and enables retrieval/reuse of patterns. Claude generates execution plans, LangGraph orchestrates multi-step execution, and Neo4j stores the resulting workflow graph.

## Tech Stack

- **Frontend:** React 18, Next.js 14, TypeScript
- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Pydantic 2, Alembic migrations
- **Orchestration/AI:** LangGraph, Anthropic Claude API
- **Databases:** PostgreSQL (relational data), Neo4j (execution graphs), Redis (plan cache)
- **Auth:** JWT (stateless), bcrypt password hashing

## Status

Early-stage MVP (single-developer). The pipeline is still under active development and not yet fully wired end-to-end.

## Quick Start (5 min)

Prerequisites: Docker, Python 3.11+, Node 18+

```bash
git clone <repo>
cp .env.example .env
# Edit .env: add API_KEY

docker compose up -d
docker compose ps  # All 5 should be "Up"
curl http://localhost:8000/health  # {"status": "ok"}
```

## Services

Frontend (http://localhost:3000) | Backend (http://localhost:8000) |
PostgreSQL (5432) | Neo4j (http://localhost:7474) | Redis (6379)

Or use frontend UI.

## Environment Variables

See `.env.example` for the full list (copy to `.env` and fill in real values):

- `DATABASE_URL` - PostgreSQL connection string (asyncpg driver)
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` - Neo4j connection
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - LLM API key used by the orchestration layer
- `JWT_SECRET` - secret used to sign/verify auth tokens
- `NEXT_PUBLIC_API_URL` - backend URL the frontend calls

## Running Without Docker

Backend:
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

