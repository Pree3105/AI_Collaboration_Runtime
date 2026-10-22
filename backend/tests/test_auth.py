import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.auth.jwt_handler import create_access_token, verify_token, verify_token_dependency
from app.database import Base, get_db
from app.error_handlers import register_exception_handlers
from app.exceptions import AuthenticationError
from app.routes.auth import router as auth_router


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(auth_router)

    @app.get("/protected")
    def protected(payload: dict = Depends(verify_token_dependency)):
        return {"user_id": payload["sub"]}

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_register_success(client):
    response = client.post(
        "/auth/register", json={"email": "alice@example.com", "password": "supersecret"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "user"
    assert "access_token" in body
    assert "password" not in body


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "bob@example.com", "password": "supersecret"})
    response = client.post(
        "/auth/register", json={"email": "bob@example.com", "password": "anotherpass"}
    )
    assert response.status_code == 409


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register", json={"email": "not-an-email", "password": "supersecret"}
    )
    assert response.status_code == 422


def test_register_weak_password(client):
    response = client.post(
        "/auth/register", json={"email": "carol@example.com", "password": "short"}
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={"email": "dave@example.com", "password": "supersecret"})
    response = client.post(
        "/auth/login", json={"email": "dave@example.com", "password": "supersecret"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["user_id"] is not None


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "erin@example.com", "password": "supersecret"})
    response = client.post(
        "/auth/login", json={"email": "erin@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login", json={"email": "ghost@example.com", "password": "whatever"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_protected_route_valid_token(client):
    register_response = client.post(
        "/auth/register", json={"email": "frank@example.com", "password": "supersecret"}
    )
    token = register_response.json()["access_token"]
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_protected_route_invalid_token(client):
    response = client.get("/protected", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_protected_route_missing_token(client):
    response = client.get("/protected")
    assert response.status_code == 401


def test_verify_token_raises_custom_exception_for_bad_token():
    with pytest.raises(AuthenticationError):
        verify_token("garbage-token")


def test_create_access_token_claims():
    token = create_access_token(user_id=1, email="grace@example.com", role="admin")
    payload = verify_token(token)
    assert payload["sub"] == "1"
    assert payload["email"] == "grace@example.com"
    assert payload["role"] == "admin"
    assert "exp" in payload
