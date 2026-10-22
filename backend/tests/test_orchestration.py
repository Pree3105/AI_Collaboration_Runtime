import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.database import Base, get_db
from app.error_handlers import register_exception_handlers
from app.models import Task
from app.orchestration import nodes
from app.routes.auth import router as auth_router
from app.routes.workflows import router as workflows_router


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # completion_node persists via app.database.get_engine(); point it at this same
    # in-memory engine, and skip the Neo4j write (no live Neo4j in this environment).
    monkeypatch.setattr(nodes, "get_engine", lambda: engine)
    monkeypatch.setattr(nodes, "_save_to_neo4j", lambda state: None)

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(workflows_router)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client, TestingSessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _register(test_client, email: str) -> tuple[str, int]:
    response = test_client.post(
        "/auth/register", json={"email": email, "password": "supersecret"}
    )
    body = response.json()
    return body["access_token"], body["user_id"]


def _create_task(session_factory, user_id: int, description: str = "Ship the feature") -> int:
    session = session_factory()
    try:
        task = Task(user_id=user_id, description=description, status="pending")
        session.add(task)
        session.commit()
        session.refresh(task)
        return task.id
    finally:
        session.close()


def test_run_workflow_requires_auth(client):
    test_client, _ = client
    response = test_client.post("/workflows/run", json={"task_id": 1})
    assert response.status_code == 401


def test_get_workflow_requires_auth(client):
    test_client, _ = client
    response = test_client.get("/workflows/1")
    assert response.status_code == 401


def test_end_to_end_workflow_run_and_fetch(client):
    test_client, session_factory = client
    token, user_id = _register(test_client, "wendy@example.com")
    task_id = _create_task(session_factory, user_id)

    run_response = test_client.post(
        "/workflows/run",
        json={"task_id": task_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert run_response.status_code == 200
    run_body = run_response.json()
    assert run_body["status"] == "completed"
    workflow_id = run_body["workflow_id"]

    get_response = test_client.get(
        f"/workflows/{workflow_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["id"] == workflow_id
    assert get_body["task_id"] == task_id
    assert get_body["status"] == "completed"
    assert get_body["execution_graph"]["task_id"] == task_id


def test_run_workflow_rejects_task_owned_by_other_user(client):
    test_client, session_factory = client
    token, user_id = _register(test_client, "vic@example.com")
    other_task_id = _create_task(session_factory, user_id=user_id + 999, description="Not mine")

    response = test_client.post(
        "/workflows/run",
        json={"task_id": other_task_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_get_workflow_rejects_other_users_workflow(client):
    test_client, session_factory = client
    token, user_id = _register(test_client, "yara@example.com")
    task_id = _create_task(session_factory, user_id)

    run_response = test_client.post(
        "/workflows/run",
        json={"task_id": task_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    workflow_id = run_response.json()["workflow_id"]

    other_token, _ = _register(test_client, "zack@example.com")
    response = test_client.get(
        f"/workflows/{workflow_id}", headers={"Authorization": f"Bearer {other_token}"}
    )
    assert response.status_code == 404
