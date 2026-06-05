import logging
import os

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


logger = logging.getLogger(__name__)

VECTOR_STORE_PATH = "./vector_store"
EMBEDDING_MODEL = "gemini-embedding-001"

def get_vector_store() -> FAISS:
    """
    Loads and returns the local FAISS vector store.

    Returns:
        FAISS vector store instance.

    Raises:
        FileNotFoundError:
            If vector store does not exist.
    """

    if not os.path.exists(VECTOR_STORE_PATH):
        raise FileNotFoundError(
            f"Vector store not found at {VECTOR_STORE_PATH}"
        )

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    logger.info("Loading FAISS vector store.")

    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )