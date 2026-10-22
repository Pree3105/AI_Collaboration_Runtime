import pytest
from langgraph.pregel import Pregel

from app.orchestration import nodes
from app.orchestration.langgraph_engine import LangGraphEngine
from app.orchestration.state_schema import WorkflowState


def _base_state(**overrides) -> WorkflowState:
    state: WorkflowState = {
        "task_id": 1,
        "task_description": "Summarize the quarterly report",
        "user_id": 1,
        "status": "pending",
        "execution_plan": None,
        "execution_graph": None,
        "execution_steps": [],
        "artifacts": [],
        "error": None,
    }
    state.update(overrides)
    return state


@pytest.fixture(autouse=True)
def _stub_persistence(monkeypatch):
    """Unit tests exercise graph/node logic only; live Postgres/Neo4j are stubbed out."""
    saved = {}

    def fake_save_to_postgres(state):
        saved["postgres"] = state
        return 1

    def fake_save_to_neo4j(state):
        saved["neo4j"] = state

    monkeypatch.setattr(nodes, "_save_to_postgres", fake_save_to_postgres)
    monkeypatch.setattr(nodes, "_save_to_neo4j", fake_save_to_neo4j)
    return saved


def test_graph_compiles():
    engine = LangGraphEngine()
    assert isinstance(engine._graph, Pregel)


@pytest.mark.asyncio
async def test_state_flows_through_happy_path(_stub_persistence):
    engine = LangGraphEngine()
    final_state = await engine.run(_base_state())

    assert final_state["status"] == "completed"
    assert final_state["error"] is None
    assert final_state["execution_plan"] is not None
    assert final_state["execution_graph"] is not None
    assert len(final_state["execution_steps"]) == 1
    assert "postgres" in _stub_persistence
    assert "neo4j" in _stub_persistence


@pytest.mark.asyncio
async def test_input_validation_error_routes_to_error_handler(_stub_persistence):
    engine = LangGraphEngine()
    final_state = await engine.run(_base_state(task_description=""))

    assert final_state["status"] == "failed"
    assert final_state["error"] == "task_description is required"
    # Should never reach persistence.
    assert "postgres" not in _stub_persistence
    assert "neo4j" not in _stub_persistence


@pytest.mark.asyncio
async def test_completion_persistence_failure_routes_to_error_without_crashing(monkeypatch):
    def raising_save(state):
        raise RuntimeError("db unavailable")

    monkeypatch.setattr(nodes, "_save_to_postgres", raising_save)
    monkeypatch.setattr(nodes, "_save_to_neo4j", lambda state: None)

    engine = LangGraphEngine()
    final_state = await engine.run(_base_state())

    assert final_state["status"] == "failed"
    assert "db unavailable" in final_state["error"]


@pytest.mark.asyncio
async def test_input_node_valid_description():
    result = await nodes.input_node(_base_state(task_description="  Do the thing  "))
    assert result["task_description"] == "Do the thing"
    assert result["status"] == "validated"
    assert result["error"] is None


@pytest.mark.asyncio
async def test_planning_node_produces_default_plan():
    state = _base_state(task_description="Build a report")
    result = await nodes.planning_node(state)
    assert result["status"] == "planned"
    assert result["execution_plan"]["task_id"] == state["task_id"]
    assert len(result["execution_plan"]["steps"]) == 1


@pytest.mark.asyncio
async def test_execution_node_marks_steps_completed():
    state = _base_state(
        execution_plan={
            "task_id": 1,
            "steps": [{"step_id": "step-1", "name": "n", "description": "d", "depends_on": []}],
        }
    )
    result = await nodes.execution_node(state)
    assert result["status"] == "executed"
    assert result["execution_steps"][0]["status"] == "completed"
    assert result["execution_graph"]["nodes"] == result["execution_steps"]


@pytest.mark.asyncio
async def test_error_handler_node_preserves_error_message():
    result = await nodes.error_handler_node(_base_state(error="boom"))
    assert result["status"] == "failed"
    assert result["error"] == "boom"


@pytest.mark.asyncio
async def test_error_handler_node_defaults_when_no_error_set():
    result = await nodes.error_handler_node(_base_state(error=None))
    assert result["error"] == "Unknown error"
