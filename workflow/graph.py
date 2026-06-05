# LangGraph State Machine Graph definition
from langgraph.graph import StateGraph, END
from schemas.graph_state import AgentState

def build_workflow():
    workflow = StateGraph(AgentState)
    # TODO: Define nodes and edges using agents: guardrail, retrieval, research, response, validation
    return workflow
