# Multi-Agent RAG System

## Overview

This project is a multo agent RAG system built using LangGraph, Gemini, and FAISS.

The system processes PDF documents, creates vector embeddings, retrieves relevant content using semantic search, and generates responses grounded in the retrieved document context. Responses include source references to the supporting documents and pages.

---

## Features

* PDF document ingestion
* Document chunking and embedding generation
* FAISS-based semantic search
* Question answering over uploaded documents
* Source attribution with document and page references
* LangGraph workflow orchestration
* Query intent classification
* Retrieval quality evaluation
* Streamlit-based user interface

---

## Workflow

### Guardrail Agent

Performs input validation and basic safety checks before processing requests.

### Research Agent

Classifies query intent and generates retrieval queries when required. Also determines retrieval depth based on the query type.

### Retrieval Agent

Searches the FAISS vector store, retrieves relevant document chunks, collects source metadata, and calculates retrieval metrics.

### Response Agent

Generates answers using Gemini based on the retrieved document context.

### Validation Agent

Performs grounding checks using retrieval metrics, source coverage, and answer-context overlap before returning the final response.

---

## Tech Stack

### Language

* Python

### LLM

* Gemini

### Workflow

* LangGraph

### Retrieval Framework

* LangChain

### Vector Store

* FAISS

### Embeddings

* Gemini Embeddings (`gemini-embedding-001`)

### Interface

* Streamlit

---

## Project Structure

```text
project/
│
├── agents/
├── core/
├── ingestion/
├── prompts/
├── schemas/
├── workflow/
├── data/
├── vector_store/
└── app_ui.py
```

---

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### Add Documents

Place PDF files inside the `data/` directory.

### Create Vector Store

```bash
python ingestion/ingestion_pipeline.py
```

### Run Application

```bash
streamlit run app_ui.py
```

---

## Example Flow

```text
User Question
      ↓
Guardrail Agent
      ↓
Research Agent
      ↓
Retrieval Agent
      ↓
Response Agent
      ↓
Validation Agent
      ↓
Final Response + Sources
```
