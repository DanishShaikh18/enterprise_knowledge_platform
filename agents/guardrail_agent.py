import logging
import re

from schemas.graph_state import GraphState


logger = logging.getLogger(__name__)


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?instructions",
    r"forget\s+your\s+instructions",
    r"bypass\s+(security|guardrails|restrictions)",
    r"act\s+as\s+another\s+assistant",
]

SYSTEM_PROMPT_EXTRACTION_PATTERNS = [
    r"show\s+(your|the)\s+system\s+prompt",
    r"reveal\s+(your|the)\s+instructions",
    r"repeat\s+your\s+hidden\s+prompt",
    r"print\s+your\s+system\s+prompt",
    r"show\s+internal\s+instructions",
]

AGENT_MANIPULATION_PATTERNS = [
    r"tell\s+the\s+response\s+agent",
    r"tell\s+the\s+retrieval\s+agent",
    r"tell\s+the\s+research\s+agent",
    r"skip\s+validation",
    r"disable\s+guardrails",
    r"bypass\s+validation",
]

OFF_TOPIC_PATTERNS = [
    r"tell\s+me\s+a\s+joke",
    r"write\s+me\s+a\s+poem",
    r"write\s+a\s+story",
    r"create\s+a\s+game",
    r"solve\s+this\s+leetcode",
    r"build\s+a\s+react\s+app",
]


def _matches_any_pattern(
    text: str,
    patterns: list[str]
) -> bool:
    """
    Returns True if any regex pattern matches.
    """

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def _is_garbage_input(
    question: str
) -> bool:
    """
    Detect empty or meaningless input.
    """

    stripped = question.strip()

    if not stripped:
        return True

    if len(stripped) < 3:
        return True

    alphanumeric_count = sum(
        char.isalnum()
        for char in stripped
    )

    return alphanumeric_count < 2


def guardrail_agent(
    state: GraphState
) -> dict:
    """
    Enterprise Guardrail Agent.

    Responsibilities:
    - Prompt injection detection
    - System prompt extraction prevention
    - Agent manipulation prevention
    - Basic off-topic filtering
    - Garbage input detection

    No LLM calls.
    No API cost.
    """

    question = state.get(
        "question",
        ""
    )

    normalized_question = (
        question
        .lower()
        .strip()
    )

    logger.info(
        "Running guardrail checks."
    )

    # ----------------------------------
    # Empty / Garbage Input
    # ----------------------------------

    if _is_garbage_input(
        normalized_question
    ):
        return {
            "is_allowed": False,
            "guardrail_reason":
                "Empty or invalid input."
        }

    # ----------------------------------
    # Prompt Injection
    # ----------------------------------

    if _matches_any_pattern(
        normalized_question,
        PROMPT_INJECTION_PATTERNS
    ):
        return {
            "is_allowed": False,
            "guardrail_reason":
                "Prompt injection attempt detected."
        }

    # ----------------------------------
    # System Prompt Extraction
    # ----------------------------------

    if _matches_any_pattern(
        normalized_question,
        SYSTEM_PROMPT_EXTRACTION_PATTERNS
    ):
        return {
            "is_allowed": False,
            "guardrail_reason":
                "System prompt extraction attempt detected."
        }

    # ----------------------------------
    # Agent Manipulation
    # ----------------------------------

    if _matches_any_pattern(
        normalized_question,
        AGENT_MANIPULATION_PATTERNS
    ):
        return {
            "is_allowed": False,
            "guardrail_reason":
                "Agent manipulation attempt detected."
        }

    # ----------------------------------
    # Off Topic
    # ----------------------------------

    if _matches_any_pattern(
        normalized_question,
        OFF_TOPIC_PATTERNS
    ):
        return {
            "is_allowed": False,
            "guardrail_reason":
                "Request is outside enterprise knowledge scope."
        }

    logger.info(
        "Guardrail checks passed."
    )

    return {
        "is_allowed": True,
        "guardrail_reason": None
    }