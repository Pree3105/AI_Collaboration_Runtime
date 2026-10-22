from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_neo4j
from app.error_handlers import register_exception_handlers
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.workflows import router as workflows_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_neo4j()
    yield

app = FastAPI(title="AI Orchestration Runtime", version="0.1.0", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(workflows_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Orchestration Runtime API"}


@app.get("/health")
async def health():
    return {"status": "ok"}
