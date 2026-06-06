import logging
import re

from schemas.graph_state import GraphState


logger = logging.getLogger(__name__)


MIN_ANSWER_LENGTH = 30
MIN_OVERLAP_RATIO = 0.20

STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "to",
    "of",
    "in",
    "for",
    "and",
    "or",
    "that",
    "this",
    "with",
    "on",
    "at",
    "by",
    "from",
}


def extract_keywords(text: str) -> set[str]:

    words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        text.lower()
    )

    return {
        word
        for word in words
        if word not in STOPWORDS
    }


def validation_agent(
    state: GraphState
) -> dict:

    retrieved_context = state.get(
        "retrieved_context",
        []
    )

    retrieval_sources = state.get(
        "retrieval_sources",
        []
    )

    answer = state.get(
        "generated_answer",
        ""
    )

    best_score = state.get(
        "best_match_score"
    )

    average_score = state.get(
        "average_match_score"
    )

    retrieved_count = state.get(
        "retrieved_document_count",
        0
    )

    # ----------------------------------
    # Hard Fail Checks
    # ----------------------------------

    if not retrieved_context:

        return {
            "validation_passed": False,
            "requires_regeneration": False,
            "validation_feedback":
                "No supporting context retrieved.",
            "confidence_score": 0.0,
        }

    if not retrieval_sources:

        return {
            "validation_passed": False,
            "requires_regeneration": False,
            "validation_feedback":
                "No source attribution available.",
            "confidence_score": 0.0,
        }

    if not answer:

        return {
            "validation_passed": False,
            "requires_regeneration": True,
            "validation_feedback":
                "Answer generation failed.",
            "confidence_score": 0.0,
        }

    if len(answer) < MIN_ANSWER_LENGTH:

        return {
            "validation_passed": False,
            "requires_regeneration": True,
            "validation_feedback":
                "Generated answer too short.",
            "confidence_score": 0.0,
        }

    # ----------------------------------
    # Keyword Overlap
    # ----------------------------------

    answer_keywords = extract_keywords(
        answer
    )

    context_keywords = extract_keywords(
        " ".join(retrieved_context)
    )

    if answer_keywords:

        overlap_ratio = (
            len(
                answer_keywords.intersection(
                    context_keywords
                )
            )
            /
            len(answer_keywords)
        )

    else:

        overlap_ratio = 0.0

    # ----------------------------------
    # Confidence Calculation
    # ----------------------------------

    confidence = 0.0

    # Overlap contribution
    confidence += overlap_ratio * 0.5

    # Retrieval score contribution
    if best_score is not None:

        retrieval_confidence = max(
            0.0,
            1.0 - min(best_score, 1.0)
        )

        confidence += retrieval_confidence * 0.3

    # Evidence contribution
    confidence += min(
        retrieved_count / 5,
        1.0
    ) * 0.2

    confidence = round(
        min(confidence, 1.0),
        2
    )

    # ----------------------------------
    # Pass / Fail
    # ----------------------------------

    validation_passed = (
        overlap_ratio >= MIN_OVERLAP_RATIO
    )

    return {
        "validation_passed":
            validation_passed,

        "requires_regeneration":
            False,

        "validation_feedback":
            None
            if validation_passed
            else "Low answer-context overlap detected.",

        "confidence_score":
            confidence,
    }