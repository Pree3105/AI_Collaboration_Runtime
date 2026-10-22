from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models import Task, Workflow


def get_workflow(db: Session, user_id: int, workflow_id: int) -> Workflow:
    workflow = (
        db.query(Workflow)
        .join(Task, Workflow.task_id == Task.id)
        .filter(Workflow.id == workflow_id, Task.user_id == user_id)
        .first()
    )
    if workflow is None:
        raise NotFoundError("Workflow not found")

    return workflow
