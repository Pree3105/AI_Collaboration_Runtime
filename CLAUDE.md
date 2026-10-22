# CLAUDE.md - Project Structure & Architecture

## System Overview

AI Collaboration Runtime + Organizational Memory Platform. Captures engineering workflows as Execution Graphs (DAGs), stores them persistently, and enables retrieval/reuse of patterns. When a user submits a task, Claude AI generates execution plans, LangGraph orchestrates multi-step execution, and Neo4j stores the complete workflow graph for future retrieval and learning.

4-week project, single developer. Demonstrates AI orchestration, multi-database persistence, LLM integration, and full-stack development.

## Architecture Diagram

┌─────────────────────────────────────────────┐
│ React 18 + Next.js (Port 3000) │
│ Login | Submit Task | Workflow History │
└──────────────────────┬──────────────────────┘
│ HTTP/JSON
↓
┌─────────────────────────────────────────────┐
│ FastAPI Backend (Port 8000) │
├─────────────────────────────────────────────┤
│ Routes: /auth, /tasks, /workflows │
│ Services: Task, Planning, Workflow │
│ LangGraph: 5-node state machine │
└──────────────────────┬──────────────────────┘
│ │ │
↓ ↓ ↓
PostgreSQL Neo4j (Graph) Redis (Cache)
(ACID Data) (Execution (5-min TTL
Tasks, Graphs) Plans)
Users


## Folder Structure

root/
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── .env.example
│
├── backend/
│ ├── requirements.txt
│ ├── main.py
│ └── app/
│ ├── config.py
│ ├── exceptions.py
│ ├── models.py
│ ├── schemas.py
│ ├── database.py
│ ├── auth/ (password_utils.py, jwt_handler.py)
│ ├── routes/ (auth.py, tasks.py, workflows.py) — thin: request/response wiring only, no DB or business logic
│ ├── services/ — all business logic lives here, grouped into one folder per topic
│ │ ├── auth/ (registration.py, login.py, tokens.py)
│ │ ├── tasks/ (queries.py, mutations.py)
│ │ └── workflows/ (execution.py, retrieval.py, planning.py)
│ ├── error_handlers.py (maps AIRuntimeException subclasses to HTTP responses)
│ ├── orchestration/ (state_schema.py, langgraph_engine.py, nodes.py)
│ └── tests/
│
├── frontend/
│ ├── package.json
│ ├── tsconfig.json
│ ├── next.config.js
│ └── src/
│ ├── pages/ (index, login, tasks, workflows)
│ ├── components/ (Header, TaskForm, WorkflowCard)
│ ├── hooks/ (useAuth, useApi)
│ ├── utils/ (api.ts, auth.ts)
│ └── tests/
│
└── prompts/ (backend-feature.md, frontend-feature.md, ai_component.md)


## Database Schema

PostgreSQL: users (id, email, hashed_password, role), tasks (id, user_id, description, status, created_at, updated_at), workflows (id, task_id, execution_graph_json, status, neo4j_graph_id), artifacts (id, workflow_id, name, artifact_type, data JSON)

Neo4j: Nodes (Task, ExecutionStep, Decision), Edges (HAS_STEPS, REQUIRES_DECISION, DEPENDS_ON)

Redis: plan:{task_id}:v1 (5-min TTL), job:queue, session:*

## Key Technologies

Frontend: React 18, Next.js 14, TypeScript (strict)
Backend: FastAPI 0.109, SQLAlchemy 2.0, Pydantic 2.5
Databases: PostgreSQL 15, Neo4j 5.14, Redis 7
AI: Claude API (Sonnet 5), LangGraph 0.0.24
Auth: JWT (stateless), bcrypt (hashing)

## Coding Rules

TypeScript/React: strict mode, type all functions, functional components with hooks, use @/ paths

Python/FastAPI: async/await for I/O, Pydantic validation, SQLAlchemy ORM, custom exceptions, pytest

Database: PostgreSQL indexes on status/created_at, Neo4j constraints, Redis namespace prefixes

General: No hardcoded values, never commit .env, test with code, meaningful names, follow patterns

## Development Workflow

1. Understand existing implementation (read CLAUDE.md, review code, docker compose up)
2. Plan changes (use /prompts/ template, outline files, identify tests)
3. Implement (follow 10-part prompt, commit frequently [Module] Description)
4. Run tests (pytest -v --cov=app tests/, npm run test)
5. Review and commit (git diff, all tests passing)

## Checklist

Before: docker compose up -d, read CLAUDE.md, review code, .env configured
After: pytest passing, npm run lint passing, git diff reviewed, commit formatted, services running

## Important

- Never commit .env (use .env.example)
- All routes require JWT or public decorator
- Users access only own tasks/workflows
- async/await required in FastAPI
- Test DB: in-memory SQLite, Production: PostgreSQL

## Commands

docker compose up -d, docker compose logs -f backend, docker compose down -v
pip install -r requirements.txt --break-system-packages, uvicorn app.main:app --reload, pytest -v --cov=app tests/
npm install, npm run dev, npm run test