from sqlalchemy.orm import Session

from app.auth.password_utils import verify_password
from app.exceptions import AuthenticationError
from app.models import User
from app.schemas import UserCreate


def authenticate_user(db: Session, payload: UserCreate) -> User:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")

    return user
