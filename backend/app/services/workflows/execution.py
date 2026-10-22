from sqlalchemy.orm import Session

from app.exceptions import ExecutionError, NotFoundError
from app.models import Task, Workflow
from app.orchestration.langgraph_engine import LangGraphEngine
from app.orchestration.state_schema import WorkflowState

_engine = LangGraphEngine()


async def run_workflow(db: Session, user_id: int, task_id: int) -> dict:
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == user_id)
        .first()
    )
    if task is None:
        raise NotFoundError("Task not found")

    initial_state: WorkflowState = {
        "task_id": task.id,
        "task_description": task.description,
        "user_id": user_id,
        "status": "pending",
        "execution_plan": None,
        "execution_graph": None,
        "execution_steps": [],
        "artifacts": [],
        "error": None,
    }
    final_state = await _engine.run(initial_state)

    workflow = (
        db.query(Workflow)
        .filter(Workflow.task_id == task.id)
        .order_by(Workflow.id.desc())
        .first()
    )
    if workflow is None:
        raise ExecutionError(final_state.get("error") or "Workflow run failed")

    task.status = final_state.get("status", task.status)
    db.commit()

    return {"workflow_id": workflow.id, "status": final_state.get("status")}
