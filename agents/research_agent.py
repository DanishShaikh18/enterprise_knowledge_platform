import logging

from core.llm import get_llm
from prompts.research_prompt import RESEARCH_SYSTEM_PROMPT
from schemas.agent_outputs import ResearchAgentOutput
from schemas.graph_state import GraphState


logger = logging.getLogger(__name__)


COMPLEX_KEYWORDS = {
    "compare",
    "comparison",
    "difference",
    "different",
    "summarize",
    "summary",
    "analyze",
    "analysis",
    "advantages",
    "disadvantages",
    "pros",
    "cons",
    "evaluate",
    "evaluation",
    "impact",
    "implications",
}


def is_complex_query(question: str) -> bool:
    """
    Determines whether the question requires
    query planning and rewriting.

    Simple factual lookups should not consume
    an additional Gemini call.
    """

    question_lower = question.lower()

    return any(
        keyword in question_lower
        for keyword in COMPLEX_KEYWORDS
    )


def classify_simple_intent(question: str) -> str:
    """
    Lightweight intent classification
    without an LLM call.
    """

    question_lower = question.lower()

    if any(
        keyword in question_lower
        for keyword in [
            "compare",
            "difference",
            "different"
        ]
    ):
        return "comparative"

    if any(
        keyword in question_lower
        for keyword in [
            "summary",
            "summarize"
        ]
    ):
        return "summary"

    return "policy_lookup"


def determine_retrieval_depth(
    intent: str
) -> int:
    """
    Controls how much evidence Retrieval Agent
    should fetch.

    Simple factual questions require fewer chunks.
    Summaries/comparisons require more.
    """

    if intent == "comparative":
        return 12

    if intent == "summary":
        return 10

    return 5


def research_agent(
    state: GraphState
) -> dict:
    """
    Hybrid Research Agent.

    Responsibilities:
    - Intent classification
    - Query planning
    - Query rewriting (when needed)
    - Retrieval strategy selection

    Uses Gemini only for complex questions.
    """

    question = state.get(
        "question",
        ""
    ).strip()

    if not question:

        logger.warning(
            "Research Agent received an empty question."
        )

        return {
            "query_intent": "unknown",
            "search_queries": [],
            "retrieval_k": 5,
        }

    try:

        # ----------------------------------
        # SIMPLE QUESTIONS
        # ----------------------------------

        if not is_complex_query(question):

            intent = classify_simple_intent(
                question
            )

            logger.info(
                "Simple query detected. "
                "Skipping LLM research step."
            )

            return {
                "query_intent": intent,
                "search_queries": [question],
                "retrieval_k": determine_retrieval_depth(
                    intent
                ),
            }

        # ----------------------------------
        # COMPLEX QUESTIONS
        # ----------------------------------

        logger.info(
            "Complex query detected. "
            "Running Research Agent."
        )

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
                ),
            ]
        )

        return {
            "query_intent":
                response.query_intent,

            "search_queries":
                response.search_queries,

            "retrieval_k":
                determine_retrieval_depth(
                    response.query_intent
                ),
        }

    except Exception as exc:

        logger.exception(
            "Research Agent failed: %s",
            exc
        )

        return {
            "query_intent": "unknown",
            "search_queries": [question],
            "retrieval_k": 5,
        }