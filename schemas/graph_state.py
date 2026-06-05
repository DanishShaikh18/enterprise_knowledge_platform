# State schema for LangGraph
from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    query: str
    contexts: List[Dict]
    is_compliant: bool
    research_notes: str
    response: str
    is_valid: bool
