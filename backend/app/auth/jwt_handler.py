from datetime import datetime, timedelta, timezone
from typing import Any
from app.models import User

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import AuthenticationError

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

_bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(user:User) -> str:
    now = datetime.now(timezone.utc)    
    payload = {
        "user_id": user.id,
        "org_id": user.org_id,
        "email": user.email,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
    }
    token= jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc


def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    if credentials is None:
        exc = AuthenticationError("Missing authentication token")
        raise HTTPException(
            status_code=exc.status_code, detail=exc.message, headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    try:
        return verify_token(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail=exc.message, headers={"WWW-Authenticate": "Bearer"}
        ) from exc
