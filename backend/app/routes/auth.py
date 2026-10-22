from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate
from app.services.auth.login import authenticate_user
from app.services.auth.registration import register_user
from app.services.auth.tokens import build_token_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> dict:
    user = register_user(db, payload)
    return build_token_response(user)


@router.post("/login")
def login(payload: UserCreate, db: Session = Depends(get_db)) -> dict:
    user = authenticate_user(db, payload)
    return build_token_response(user)
