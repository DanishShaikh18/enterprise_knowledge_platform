from langgraph.graph import StateGraph, START, END

from agents.guardrail_agent import guardrail_agent
from agents.research_agent import research_agent
from agents.retrieval_agent import retrieval_agent
from agents.response_agent import response_agent
from agents.validation_agent import validation_agent

from schemas.graph_state import GraphState


def route_after_guardrail(state: GraphState) -> str:
    """
    Determines whether the workflow should proceed
    or terminate after guardrail evaluation.
    """

    if state.get("is_allowed", False):
        return "research"

    return END


def route_after_validation(state: GraphState) -> str:
    """
    Determines whether the answer should be accepted
    or regenerated.
    """

    if state.get("requires_regeneration", False):
        return "response"

    return END


def build_graph():
    """
    Builds and compiles the LangGraph workflow.

    Workflow:

    START
      ↓
    Guardrail
      ↓
    Research
      ↓
    Retrieval
      ↓
    Response
      ↓
    Validation

    Validation Passed
      ↓
    END

    Validation Failed
      ↓
    Response
    """

    workflow = StateGraph(GraphState)

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    workflow.add_node(
        "guardrail",
        guardrail_agent
    )

    workflow.add_node(
        "research",
        research_agent
    )

    workflow.add_node(
        "retrieval",
        retrieval_agent
    )

    workflow.add_node(
        "response",
        response_agent
    )

    workflow.add_node(
        "validation",
        validation_agent
    )

    # --------------------------------------------------
    # Entry Point
    # --------------------------------------------------

    workflow.add_edge(
        START,
        "guardrail"
    )

    # --------------------------------------------------
    # Guardrail Routing
    # --------------------------------------------------

    workflow.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "research": "research",
            END: END
        }
    )

    # --------------------------------------------------
    # Main Workflow
    # --------------------------------------------------

    workflow.add_edge(
        "research",
        "retrieval"
    )

    workflow.add_edge(
        "retrieval",
        "response"
    )

    workflow.add_edge(
        "response",
        "validation"
    )

    # --------------------------------------------------
    # Validation Routing
    # --------------------------------------------------

    workflow.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "response": "response",
            END: END
        }
    )

    return workflow.compile()


app = build_graph()