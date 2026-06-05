import logging

from core.llm import get_llm
from prompts.response_prompt import RESPONSE_SYSTEM_PROMPT
from schemas.agent_outputs import ResponseAgentOutput
from schemas.graph_state import GraphState


logger = logging.getLogger(__name__)


def response_agent(state: GraphState) -> dict:
    """
    LangGraph Response Agent.

    Responsibilities:
    - Generate a grounded answer.
    - Use only retrieved evidence.
    - Avoid hallucinations.
    - Produce an answer for validation.

    This agent does NOT:
    - Retrieve documents.
    - Validate answers.
    - Generate citations.
    - Perform workflow routing.

    Returns:
        State updates containing:
        - generated_answer
    """

    question = state.get("question", "").strip()

    retrieved_context = state.get(
        "retrieved_context",
        []
    )

    if not question:
        logger.warning(
            "Response Agent received an empty question."
        )

        return {
            "generated_answer": (
                "No question was provided."
            )
        }

    if not retrieved_context:
        logger.warning(
            "No retrieved context available."
        )

        return {
            "generated_answer": (
                "I could not find sufficient information "
                "in the available documents to answer "
                "this question."
            )
        }

    try:

        logger.info(
            "Generating grounded response."
        )

        llm = get_llm(
            temperature=0
        ).with_structured_output(
            ResponseAgentOutput
        )

        context = "\n\n".join(
            retrieved_context
        )

        prompt = f"""
Question:
{question}

Retrieved Context:
{context}
"""

        response: ResponseAgentOutput = llm.invoke(
            [
                (
                    "system",
                    RESPONSE_SYSTEM_PROMPT
                ),
                (
                    "human",
                    prompt
                )
            ]
        )

        logger.info(
            "Response generated successfully."
        )

        return {
            "generated_answer":
                response.generated_answer
        }

    except Exception as exc:

        logger.exception(
            "Response generation failed: %s",
            exc
        )

        return {
            "generated_answer": (
                "An error occurred while generating "
                "the response."
            )
        }