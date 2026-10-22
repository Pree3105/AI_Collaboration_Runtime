from sqlalchemy.orm import Session

from app.models import Task
from app.schemas import TaskCreate


def create_task(db: Session, user_id: int, payload: TaskCreate) -> Task:
    task = Task(user_id=user_id, description=payload.description)
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
    except Exception:
        db.rollback()
        raise
    return task
