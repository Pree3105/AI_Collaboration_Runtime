from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.jwt_handler import verify_token_dependency
from app.database import get_db
from app.services.workflows.execution import run_workflow
from app.services.workflows.retrieval import get_workflow

router = APIRouter(prefix="/workflows", tags=["workflows"])


class WorkflowRunRequest(BaseModel):
    task_id: int


@router.post("/run")
async def run(
    payload: WorkflowRunRequest,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token_dependency),
) -> dict:
    user_id = int(token_payload["sub"])
    return await run_workflow(db, user_id, payload.task_id)


@router.get("/{workflow_id}")
def get(
    workflow_id: int,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token_dependency),
) -> dict:
    user_id = int(token_payload["sub"])
    workflow = get_workflow(db, user_id, workflow_id)
    return {
        "id": workflow.id,
        "task_id": workflow.task_id,
        "status": workflow.status,
        "execution_graph": workflow.execution_graph_json,
        "created_at": workflow.created_at,
    }
