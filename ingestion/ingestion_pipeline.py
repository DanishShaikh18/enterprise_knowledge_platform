import os
import sys
import glob
import logging
from typing import List
from dotenv import load_dotenv
import shutil

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Configuration Constants
DATA_DIR = "./data"
VECTOR_STORE_DIR = "./vector_store"
EMBEDDING_MODEL = "models/text-embedding-004"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def setup_logger() -> logging.Logger:
    """
    Configures and returns a logger for the ingestion pipeline.
    """
    logger = logging.getLogger("ingestion_pipeline")
    logger.setLevel(logging.INFO)
    
    # Create console handler with a standardized format
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(ch)
        
    return logger

def validate_environment(logger: logging.Logger) -> None:
    """
    Validates required environment variables and directory structures.
    Exits the script if critical requirements are missing.
    """
    # Validate API Key
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY environment variable is not set. Please check your .env file.")
        sys.exit(1)
        
    # Validate Data Directory
    if not os.path.exists(DATA_DIR):
        logger.error(f"Data directory '{DATA_DIR}' does not exist.")
        sys.exit(1)
        
    # Validate PDFs exist in the directory
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in '{DATA_DIR}'. Please add documents before running ingestion.")
        sys.exit(1)
        
    logger.info(f"Environment validated successfully. Found {len(pdf_files)} PDF(s) to process.")

def load_documents(logger: logging.Logger) -> List[Document]:
    """
    Loads all PDF documents from the configured data directory.
    PyPDFDirectoryLoader automatically populates 'source' and 'page' metadata.
    """
    try:
        logger.info(f"Loading PDFs from {DATA_DIR}...")
        loader = PyPDFDirectoryLoader(DATA_DIR)
        documents = loader.load()
        
        # Calculate unique PDFs loaded based on metadata
        unique_sources = set(doc.metadata.get('source', 'Unknown') for doc in documents)
        
        logger.info(f"Successfully loaded {len(unique_sources)} PDF(s).")
        logger.info(f"Total pages extracted: {len(documents)}")
        
        return documents
    except Exception as e:
        logger.error(f"Failed to load documents: {e}", exc_info=True)
        sys.exit(1)

def chunk_documents(documents: List[Document], logger: logging.Logger) -> List[Document]:
    """
    Splits loaded documents into smaller, manageable chunks for embedding.
    """
    try:
        logger.info(f"Chunking documents (Size: {CHUNK_SIZE}, Overlap: {CHUNK_OVERLAP})...")
        
        # We use RecursiveCharacterTextSplitter because it respects natural language 
        # boundaries (paragraphs, sentences) before resorting to harsh character limits.
        # The 200 character overlap prevents loss of context between sequential chunks.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Successfully created {len(chunks)} chunks.")
        
        return chunks
    except Exception as e:
        logger.error(f"Failed to chunk documents: {e}", exc_info=True)
        sys.exit(1)

def create_and_save_vector_store(chunks: List[Document], logger: logging.Logger) -> None:
    """
    Generates embeddings for chunks and saves them locally using FAISS.
    Overwrites the existing vector store if it already exists.
    """
    try:
        logger.info(f"Initializing Google embeddings model: {EMBEDDING_MODEL}...")
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        
        logger.info("Generating vectors and building FAISS index (This may take a moment)...")
        # Initialize FAISS with chunks and embeddings
        vector_store = FAISS.from_documents(chunks, embeddings)
        
        logger.info(f"Saving vector store locally to '{VECTOR_STORE_DIR}'...")
        # Save local will overwrite existing index/pkl files in the directory cleanly
        if os.path.exists(VECTOR_STORE_DIR):
            shutil.rmtree(VECTOR_STORE_DIR)
        
        logger.info("Vector store creation and persistence successful.")
    except Exception as e:
        logger.error(f"Failed to create or save vector store: {e}", exc_info=True)
        sys.exit(1)

def main() -> None:
    """
    Main execution pipeline for document ingestion.
    """
    # Load environment variables (e.g., from .env file)
    load_dotenv()
    
    logger = setup_logger()
    logger.info("Starting Enterprise Knowledge Platform Ingestion Pipeline...")
    
    # 1. Validate Setup
    validate_environment(logger)
    
    # 2. Extract Data
    documents = load_documents(logger)
    
    if not documents:
        logger.warning("No text extracted from the PDFs. Exiting pipeline.")
        sys.exit(0)
    
    # 3. Transform Data (Chunking)
    chunks = chunk_documents(documents, logger)
    
    # 4. Load Data (Embedding & Vector Storage)
    create_and_save_vector_store(chunks, logger)
    
    logger.info("Ingestion pipeline completed successfully.")

if __name__ == "__main__":
    main()