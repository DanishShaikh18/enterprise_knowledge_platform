import logging

from core.llm import get_llm
from prompts.guardrail_prompt import GUARDRAIL_SYSTEM_PROMPT
from schemas.agent_outputs import GuardrailAgentOutput
from schemas.graph_state import GraphState


logger = logging.getLogger(__name__)


def guardrail_agent(state: GraphState) -> dict:
    """
    LangGraph Guardrail Agent.

    Responsibilities:
    - Detect prompt injection attempts
    - Detect jailbreak attempts
    - Detect system prompt extraction attempts
    - Detect workflow manipulation attempts
    - Detect irrelevant requests

    Returns only the state updates required
    by downstream agents.
    """

    question = state.get("question", "").strip()

    if not question:
        return {
            "is_allowed": False,
            "guardrail_reason": "Empty question received."
        }

    try:
        logger.info("Running guardrail evaluation.")

        llm = get_llm(
            temperature=0
        ).with_structured_output(
            GuardrailAgentOutput
        )

        response: GuardrailAgentOutput = llm.invoke(
            [
                (
                    "system",
                    GUARDRAIL_SYSTEM_PROMPT
                ),
                (
                    "human",
                    question
                )
            ]
        )

        logger.info(
            "Guardrail result: allowed=%s",
            response.is_allowed
        )

        return {
            "is_allowed": response.is_allowed,
            "guardrail_reason": response.guardrail_reason
        }

    except Exception as exc:
        logger.exception(
            "Guardrail evaluation failed: %s",
            exc
        )

        # Fail closed.
        # If the security layer fails,
        # downstream agents should not execute.
        return {
            "is_allowed": False,
            "guardrail_reason": (
                "Guardrail evaluation failed."
            )
        }