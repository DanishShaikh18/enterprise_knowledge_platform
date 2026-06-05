import logging

from core.llm import get_llm
from prompts.validation_prompt import VALIDATION_SYSTEM_PROMPT
from schemas.agent_outputs import ValidationAgentOutput
from schemas.graph_state import GraphState


logger = logging.getLogger(__name__)

MAX_REGENERATION_ATTEMPTS = 3


def validation_agent(state: GraphState) -> dict:
    """
    LangGraph Validation Agent.

    Responsibilities:
    - Verify answer grounding.
    - Detect hallucinations.
    - Detect unsupported claims.
    - Determine whether regeneration is required.
    - Prevent infinite regeneration loops.

    This agent does NOT:
    - Generate answers.
    - Retrieve documents.
    - Modify retrieved context.

    Returns:
        State updates containing:
        - validation_passed
        - validation_feedback
        - requires_regeneration
        - regeneration_count
    """

    question = state.get("question", "").strip()

    generated_answer = state.get(
        "generated_answer",
        ""
    )

    retrieved_context = state.get(
        "retrieved_context",
        []
    )

    regeneration_count = state.get(
        "regeneration_count",
        0
    )

    if not generated_answer:

        logger.warning(
            "Validation Agent received empty answer."
        )

        return {
            "validation_passed": False,
            "validation_feedback": (
                "No answer was generated."
            ),
            "requires_regeneration": True,
            "regeneration_count": regeneration_count + 1
        }

    try:

        logger.info(
            "Running answer validation."
        )

        llm = get_llm(
            temperature=0
        ).with_structured_output(
            ValidationAgentOutput
        )

        context = "\n\n".join(
            retrieved_context
        )

        validation_input = f"""
Question:
{question}

Retrieved Context:
{context}

Generated Answer:
{generated_answer}
"""

        result: ValidationAgentOutput = llm.invoke(
            [
                (
                    "system",
                    VALIDATION_SYSTEM_PROMPT
                ),
                (
                    "human",
                    validation_input
                )
            ]
        )

        # --------------------------------------------------
        # Retry Limit Protection
        # --------------------------------------------------

        if (
            result.requires_regeneration
            and regeneration_count >= MAX_REGENERATION_ATTEMPTS
        ):

            logger.warning(
                "Maximum regeneration attempts reached."
            )

            return {
                "validation_passed": False,
                "validation_feedback": (
                    "Maximum regeneration attempts reached."
                ),
                "requires_regeneration": False,
                "regeneration_count": regeneration_count
            }

        # --------------------------------------------------
        # Validation Failed
        # --------------------------------------------------

        if result.requires_regeneration:

            logger.info(
                "Validation failed. Regeneration required."
            )

            return {
                "validation_passed": False,
                "validation_feedback":
                    result.validation_feedback,
                "requires_regeneration": True,
                "regeneration_count":
                    regeneration_count + 1
            }

        # --------------------------------------------------
        # Validation Passed
        # --------------------------------------------------

        logger.info(
            "Validation successful."
        )

        return {
            "validation_passed": True,
            "validation_feedback": None,
            "requires_regeneration": False,
            "regeneration_count":
                regeneration_count
        }

    except Exception as exc:

        logger.exception(
            "Validation Agent failed: %s",
            exc
        )

        return {
            "validation_passed": False,
            "validation_feedback": (
                "Validation process failed."
            ),
            "requires_regeneration": True,
            "regeneration_count":
                regeneration_count + 1
        }