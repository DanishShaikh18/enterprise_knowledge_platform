import logging
import os
import sys

# Add root folder to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from workflow.graph import app


logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="Enterprise AI Knowledge Platform",
    page_icon="📚",
    layout="wide"
)


def initialize_session_state() -> None:
    """
    Initializes Streamlit session state variables.
    """

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def render_sources(sources) -> None:
    """
    Renders retrieved source metadata.
    """

    if not sources:
        return

    st.subheader("Sources")

    for source in sources:

        document_name = getattr(
            source,
            "document_name",
            "Unknown"
        )

        page_number = getattr(
            source,
            "page_number",
            "Unknown"
        )

        st.markdown(
            f"- **{document_name}** (Page {page_number})"
        )


def main() -> None:

    initialize_session_state()

    st.title(
        "Enterprise AI Knowledge Platform"
    )

    st.caption(
        "LangGraph • Multi-Agent RAG • Gemini • FAISS"
    )

    user_question = st.text_input(
        "Ask a question about your documents:"
    )

    ask_button = st.button(
        "Submit"
    )

    if ask_button and user_question:

        with st.spinner(
            "Running multi-agent workflow..."
        ):

            try:

                result = app.invoke(
                    {
                        "question": user_question,
                        "regeneration_count": 0
                    }
                )

                st.subheader("Answer")

                st.write(
                    result.get(
                        "generated_answer",
                        "No answer generated."
                    )
                )

                render_sources(
                    result.get(
                        "retrieval_sources",
                        []
                    )
                )

                with st.expander(
                    "Workflow Trace"
                ):

                    st.json(
                        {
                            "is_allowed":
                                result.get(
                                    "is_allowed"
                                ),

                            "query_intent":
                                result.get(
                                    "query_intent"
                                ),

                            "validation_passed":
                                result.get(
                                    "validation_passed"
                                ),

                            "regeneration_count":
                                result.get(
                                    "regeneration_count"
                                )
                        }
                    )

            except Exception as exc:

                logger.exception(
                    "Workflow execution failed: %s",
                    exc
                )

                st.error(
                    "An error occurred while processing your request."
                )


if __name__ == "__main__":
    main()