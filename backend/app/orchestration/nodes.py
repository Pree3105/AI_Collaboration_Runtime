import logging
from typing import Any

from app.database import SessionLocal, get_engine
from app.models import Workflow
from app.orchestration.state_schema import WorkflowState
from app.services.workflows.planning import PlanningService
from neo4j import GraphDatabase
from app.config import settings

logger = logging.getLogger(__name__)

#input_node,gets initial_state of WorkflowState ,check if task_description is present in state, if not return failed status with error message, 
# else return validated status with task_description and empty execution_steps and artifacts
async def input_node(state: WorkflowState) -> dict[str, Any]:
    description = (state.get("task_description") or "").strip()
    if not description:
        return {"status": "failed", "error": "task_description is required"}

    return {
        "task_description": description,
        "status": "validated",
        "execution_steps": state.get("execution_steps") or [],
        "artifacts": state.get("artifacts") or [],
        "error": None,
    }

#planning_node, gets the validated state, creates an execution plan based on the task description, and returns execution_plan with a status:planned
async def planning_node(state: WorkflowState) -> dict[str, Any]:
    try:
        service = PlanningService()
        plan = await service.generate_plan(state["task_description"], state["task_id"])
        return {"execution_plan": plan.model_dump(), "status": "planned"}
    except Exception as exc:  # noqa: BLE001
        logger.exception("planning_node failed for task_id=%s", state.get("task_id"))
        return {"status": "failed", "error": str(exc)}

# execution_node, gets the planned state, executes the steps in the execution plan, and returns execution_steps and execution_graph with a status:executed
async def execution_node(state: WorkflowState) -> dict[str, Any]:
    try:
        plan = state.get("execution_plan") or {}
        steps = [{**step, "status": "completed"} for step in plan.get("steps", [])]
        execution_graph = {"task_id": state["task_id"], "nodes": steps, "edges": []}
        return {
            "execution_steps": steps,
            "execution_graph": execution_graph,
            "status": "executed",
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("execution_node failed for task_id=%s", state.get("task_id"))
        return {"status": "failed", "error": str(exc)}

# completion_node, gets the executed state, saves the workflow to Postgres and Neo4j, and returns a status:completed or failed with an error message
def _save_to_postgres(state: WorkflowState) -> int:
    session = SessionLocal(bind=get_engine())
    try:
        workflow = session.query(Workflow).filter(Workflow.task_id == state["task_id"]).first()
        if workflow is None:
            workflow = Workflow(task_id=state["task_id"])
            session.add(workflow)

        workflow.execution_graph_json = state.get("execution_graph") or {}
        workflow.status = "completed"
        session.commit()
        session.refresh(workflow)
        return workflow.id
    finally:
        session.close()

# gets execution_graph ->nodes/steps from it, connects to Neo4j, and saves the task and execution steps with their dependencies and decisions to the graph database
def _save_to_neo4j(state: WorkflowState) -> None:
    execution_graph = state.get("execution_graph") or {}
    steps = execution_graph.get("nodes", [])

    driver = GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    try:
        with driver.session() as session:
            session.run(
                "MERGE (t:Task {id: $task_id}) SET t.status = $status",
                task_id=state["task_id"],
                status=state.get("status", "completed"),
            )
            for step in steps:
                session.run(
                    """
                    MATCH (t:Task {id: $task_id})
                    MERGE (s:ExecutionStep {id: $step_id})
                    SET s.name = $name, s.description = $description, s.status = $status
                    MERGE (t)-[:HAS_STEPS]->(s)
                    """,
                    task_id=state["task_id"],
                    step_id=step.get("step_id"),
                    name=step.get("name"),
                    description=step.get("description"),
                    status=step.get("status", "pending"),
                )
                for dep_id in step.get("depends_on", []):
                    session.run(
                        """
                        MATCH (s:ExecutionStep {id: $step_id})
                        MATCH (dep:ExecutionStep {id: $dep_id})
                        MERGE (s)-[:DEPENDS_ON]->(dep)
                        """,
                        step_id=step.get("step_id"),
                        dep_id=dep_id,
                    )
                if step.get("requires_decision"):
                    session.run(
                        """
                        MATCH (s:ExecutionStep {id: $step_id})
                        MERGE (d:Decision {id: $decision_id})
                        MERGE (s)-[:REQUIRES_DECISION]->(d)
                        """,
                        step_id=step.get("step_id"),
                        decision_id=f"{step.get('step_id')}-decision",
                    )
    finally:
        driver.close()


async def completion_node(state: WorkflowState) -> dict[str, Any]:
    try:
        _save_to_postgres(state)
        _save_to_neo4j(state)
        return {"status": "completed", "error": None}
    except Exception as exc:  # noqa: BLE001
        logger.exception("completion_node failed to persist workflow for task_id=%s", state.get("task_id"))
        return {"status": "failed", "error": str(exc)}

# error_handler_node, gets the state with an error, logs the error, and returns a failed status with the error message
async def error_handler_node(state: WorkflowState) -> dict[str, Any]:
    error_message = state.get("error") or "Unknown error"
    logger.error("Workflow failed for task_id=%s: %s", state.get("task_id"), error_message)
    return {"status": "failed", "error": error_message}
