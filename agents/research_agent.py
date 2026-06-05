import logging

from core.llm import get_llm
from prompts.research_prompt import RESEARCH_SYSTEM_PROMPT
from schemas.agent_outputs import ResearchAgentOutput
from schemas.graph_state import GraphState


logger = logging.getLogger(__name__)


def research_agent(state: GraphState) -> dict:
    """
    LangGraph Research Agent.

    Responsibilities:
    - Understand the user's information need
    - Classify query intent
    - Generate optimized retrieval queries
    - Improve downstream retrieval quality

    This agent does NOT:
    - Retrieve documents
    - Answer questions
    - Generate citations

    Returns only the state updates required by
    downstream agents.
    """

    question = state.get("question", "").strip()

    if not question:
        logger.warning("Research Agent received an empty question.")

        return {
            "query_intent": "unknown",
            "search_queries": []
        }

    try:
        logger.info("Running research agent.")

        llm = get_llm(
            temperature=0
        ).with_structured_output(
            ResearchAgentOutput
        )

        response: ResearchAgentOutput = llm.invoke(
            [
                (
                    "system",
                    RESEARCH_SYSTEM_PROMPT
                ),
                (
                    "human",
                    question
                )
            ]
        )

        logger.info(
            "Research complete. Intent=%s | Queries=%d",
            response.query_intent,
            len(response.search_queries)
        )

        return {
            "query_intent": response.query_intent,
            "search_queries": response.search_queries
        }

    except Exception as exc:
        logger.exception(
            "Research agent failed: %s",
            exc
        )

        # Fail gracefully.
        # Retrieval can still attempt to use the
        # original question as a fallback query.
        return {
            "query_intent": "unknown",
            "search_queries": [question]
        }