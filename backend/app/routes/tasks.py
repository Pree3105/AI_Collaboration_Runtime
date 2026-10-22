from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.jwt_handler import verify_token_dependency
from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskResponse
from app.services.tasks.mutations import create_task
from app.services.tasks.queries import list_user_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token_dependency),
) -> list[Task]:
    user_id = int(token_payload["sub"])
    return list_user_tasks(db, user_id)


@router.post("", response_model=TaskResponse, status_code=201)
def create(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token_dependency),
) -> Task:
    user_id = int(token_payload["sub"])
    return create_task(db, user_id, payload)
