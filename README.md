# Enterprise Knowledge Intelligence Platform

A production-grade, multi-agent RAG system designed to query enterprise policies, compliance guidelines, and HR documents. Built with Google Gemini, LangGraph, and FAISS.

## Core Features
* **Multi-Agent Routing:** Utilizes LangGraph to route queries between a Retriever Agent, a Policy Analyst, and a Compliance Guardrail.
* **Native Tool Calling:** Agents dynamically query the vector store via tools.
* **Structured Outputs:** Enforces strict Pydantic schemas for JSON-formatted enterprise responses.
* **Traceable Execution:** Exposes the internal reasoning and state transitions of the LangGraph engine.

## Setup Instructions
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your `GOOGLE_API_KEY`.
4. Place sample policy PDFs in the `/data` directory.
5. Run the ingestion pipeline: `python ingestion_pipeline.py`
6. Start the UI: `streamlit run app_ui.py`