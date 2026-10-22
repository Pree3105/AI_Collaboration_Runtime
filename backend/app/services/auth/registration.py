from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password
from app.exceptions import ConflictError
from app.models import User
from app.schemas import UserCreate


def register_user(db: Session, payload: UserCreate) -> User:
    if db.query(User).filter(User.email == payload.email).first() is not None:
        raise ConflictError("Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
