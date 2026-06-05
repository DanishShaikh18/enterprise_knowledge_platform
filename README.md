# Enterprise Knowledge Platform

An enterprise-grade Retrieval-Augmented Generation (RAG) platform with a LangGraph state machine, semantic document chunking, FAISS local vector storage, and a Streamlit UI trace viewer.

## Directory Structure

```
enterprise_knowledge_platform/
├── data/                      # Place your raw source PDFs here (ignored by git)
├── vector_store/              # FAISS index files generated locally (ignored by git)
├── ingestion_pipeline.py      # Handles PDF parsing, semantic chunking, and FAISS indexing
├── graph_engine.py            # The core LangGraph state machine, nodes, and tool definitions
├── app_ui.py                  # The Streamlit frontend and execution trace viewer
├── requirements.txt           # Explicit version-locked dependencies
├── .env                       # Your local secrets (DO NOT COMMIT)
├── .env.example               # Template for required environment variables
├── .gitignore                 # Standard Python/GCP ignores to keep the repo clean
└── README.md                  # System architecture, setup instructions, and run commands
```

## Getting Started

### 1. Installation
Clone the repository and install dependencies in a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configuration
Copy the `.env.example` file to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### 3. Usage
1. Place raw PDF documents in the `data/` directory.
2. Run the ingestion pipeline to parse documents and generate the local FAISS index:
   ```bash
   python ingestion_pipeline.py
   ```
3. Run the Streamlit application to start the user interface:
   ```bash
   streamlit run app_ui.py
   ```
