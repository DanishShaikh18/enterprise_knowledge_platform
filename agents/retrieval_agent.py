import logging
from typing import List

from core.vector_store import get_vector_store
from schemas.agent_outputs import RetrievalSourceMetadata
from schemas.graph_state import GraphState


logger = logging.getLogger(__name__)


TOP_K_RESULTS = 5


def retrieval_agent(state: GraphState) -> dict:
    """
    LangGraph Retrieval Agent.

    Responsibilities:
    - Execute vector searches against FAISS.
    - Retrieve relevant document chunks.
    - Extract source metadata.
    - Calculate retrieval quality metrics.
    - Prepare evidence for downstream agents.

    This agent does NOT:
    - Generate answers.
    - Summarize content.
    - Perform validation.

    Returns:
        State updates containing:
        - retrieved_context
        - retrieval_sources
        - best_match_score
    """

    search_queries = state.get("search_queries", [])

    if not search_queries:
        logger.warning(
            "No search queries found. Falling back to user question."
        )

        question = state.get("question", "").strip()

        if not question:
            return {
                "retrieved_context": [],
                "retrieval_sources": [],
                "best_match_score": 0.0
            }

        search_queries = [question]

    try:
        logger.info(
            "Running retrieval agent with %d query(s).",
            len(search_queries)
        )

        vector_store = get_vector_store()

        retrieved_context: List[str] = []
        retrieval_sources: List[RetrievalSourceMetadata] = []

        best_match_score = 0.0

        # Track duplicates
        seen_chunks = set()

        for query in search_queries:

            results = vector_store.similarity_search_with_score(
                query=query,
                k=TOP_K_RESULTS
            )

            for doc, score in results:

                chunk_text = doc.page_content.strip()

                if not chunk_text:
                    continue

                # Prevent duplicate chunks
                if chunk_text in seen_chunks:
                    continue

                seen_chunks.add(chunk_text)

                retrieved_context.append(chunk_text)

                retrieval_sources.append(
                    RetrievalSourceMetadata(
                        document_name=doc.metadata.get(
                            "source",
                            "Unknown"
                        ),
                        page_number=doc.metadata.get(
                            "page",
                            0
                        )
                    )
                )

                # Depending on FAISS implementation,
                # lower score often means better match.
                #
                # We normalize by tracking the best
                # score seen and expose it to the graph.
                #
                # Interview Note:
                # This metric is only used as a rough
                # retrieval quality indicator.
                #
                if best_match_score == 0.0:
                    best_match_score = float(score)
                else:
                    best_match_score = min(
                        best_match_score,
                        float(score)
                    )

        logger.info(
            "Retrieved %d unique chunks.",
            len(retrieved_context)
        )

        return {
            "retrieved_context": retrieved_context,
            "retrieval_sources": retrieval_sources,
            "best_match_score": best_match_score
        }

    except Exception as exc:

        logger.exception(
            "Retrieval agent failed: %s",
            exc
        )

        return {
            "retrieved_context": [],
            "retrieval_sources": [],
            "best_match_score": 0.0
        }