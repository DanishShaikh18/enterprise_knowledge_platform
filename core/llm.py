import logging
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


logger = logging.getLogger(__name__)

# Load environment variables once when the module is imported
load_dotenv()


def get_llm(
    temperature: float = 0.0,
    model: str = "gemini-2.5-flash"
) -> ChatGoogleGenerativeAI:
    """
    Returns a configured Gemini LLM instance.

    This function centralizes model configuration so that
    all agents use the same initialization logic.

    Args:
        temperature: Model temperature.
        model: Gemini model name.

    Returns:
        Configured ChatGoogleGenerativeAI instance.

    Raises:
        ValueError: If GOOGLE_API_KEY is missing.
    """

    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY environment variable not found.")
        raise ValueError(
            "GOOGLE_API_KEY environment variable is required."
        )

    logger.info(
        "Initializing Gemini model: %s",
        model
    )

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
    )