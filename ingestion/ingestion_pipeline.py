# Ingestion pipeline entry point
import os
from dotenv import load_dotenv

load_dotenv()

def run_ingestion():
    print("Running document ingestion pipeline...")
    # TODO: Implement parsing, semantic chunking, and FAISS vectorization

if __name__ == "__main__":
    run_ingestion()
