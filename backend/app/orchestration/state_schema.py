from typing import Any, TypedDict


class WorkflowState(TypedDict):
    task_id: int
    task_description: str
    user_id: int
    status: str
    execution_plan: dict[str, Any] | None
    execution_graph: dict[str, Any] | None
    execution_steps: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    error: str | None
