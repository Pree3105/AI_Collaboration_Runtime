from app.auth.jwt_handler import create_access_token
from app.models import User


def build_token_response(user: User) -> dict:
    token = create_access_token(user_id=user.id, email=user.email, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
    }
