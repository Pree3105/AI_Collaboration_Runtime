from langgraph.graph import END, StateGraph
from langgraph.pregel import Pregel

from app.orchestration.nodes import (
    completion_node,
    error_handler_node,
    execution_node,
    input_node,
    planning_node,
)
from app.orchestration.state_schema import WorkflowState


def _route_on_error(state: WorkflowState) -> str:
    return "error" if state.get("error") else "continue"

#runs when /workflows/run is called, creates a StateGraph with nodes for input, planning, execution, completion, 
# and error handling, and runs the graph with the initial state. Returns the final state of the workflow.
class LangGraphEngine:
    """Wraps the workflow execution StateGraph: input -> planning -> execution -> completion,
    with any stage's error short-circuiting to error_handler instead of raising."""

    def __init__(self) -> None:
        self._graph: Pregel = self._build_graph()

    def _build_graph(self) -> Pregel:
        graph = StateGraph(WorkflowState)

        graph.add_node("input", input_node)
        graph.add_node("planning", planning_node)
        graph.add_node("execution", execution_node)
        graph.add_node("completion", completion_node)
        graph.add_node("error_handler", error_handler_node)

        graph.set_entry_point("input")
        graph.add_conditional_edges(
            "input", _route_on_error, {"error": "error_handler", "continue": "planning"}
        )
        graph.add_conditional_edges(
            "planning", _route_on_error, {"error": "error_handler", "continue": "execution"}
        )
        graph.add_conditional_edges(
            "execution", _route_on_error, {"error": "error_handler", "continue": "completion"}
        )
        graph.add_edge("completion", END)
        graph.add_edge("error_handler", END)

        return graph.compile()

    async def run(self, initial_state: WorkflowState) -> WorkflowState:
        return await self._graph.ainvoke(initial_state)
