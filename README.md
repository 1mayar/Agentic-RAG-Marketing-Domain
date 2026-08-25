# Agentic-RAG-Marketing-Domain
# Marketing Campaign Strategist Agent

## Overview

This project implements a Retrieval-Augmented Generation (RAG) based Marketing Campaign Strategist Agent using LangChain.

The agent uses a marketing book in PDF format as its knowledge source. The document is processed, split into chunks, converted into embeddings, and stored in a Chroma vector database.

For marketing-related questions, the agent retrieves relevant passages from the book and uses them as context for generating the final answer.

---

## Features

* PDF document ingestion
* Recursive text chunking
* Multilingual embeddings
* Chroma vector database
* LangChain retrieval tool
* Qwen 2.5 72B through OpenRouter
* Marketing-domain guardrails
* Arabic and English responses
* Persistent local vector database

---

## Architecture

```text
                         User Query
                              |
                              v
                    +-------------------+
                    |    LangChain LLM  |
                    +-------------------+
                              |
                    Marketing Question?
                         /          \
                       No            Yes
                       |              |
                       v              v
                 Direct Response   Retriever Tool
                                      |
                                      v
                              Chroma Vector DB
                                      |
                                      v
                              Relevant Chunks
                                      |
                                      v
                               LLM + Context
                                      |
                                      v
                                Final Answer
```

---

## Project Structure

```text
marketing-agent/
│
├── main.py
├── requirements.txt
├── README.md
├── DESIGN.md
├── .gitignore
├── markting book.pdf
│
├── chroma_db_marketing/
│
└── .env
```

The `chroma_db_marketing` directory is generated automatically after the first run and should not be committed.

The `.env` file contains the OpenRouter API key and should never be committed or submitted.

---

## Installation

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

#### Windows

```bash
.venv\Scripts\activate
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```text
OPENROUTER_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with a valid OpenRouter API key.

---

## Knowledge Source

Place the marketing PDF in the project root.

Expected filename:

```text
markting book.pdf
```

The application automatically loads the PDF and creates the vector database on the first run.

---

## Running the Agent

Run:

```bash
python main.py
```

The application will display:

```text
Type your question (or 'exit' to quit).
```

Example:

```text
User: What are effective customer segmentation strategies?
```

The agent retrieves relevant information from the marketing book and generates a grounded answer.

To stop the application:

```text
exit
```

---

## RAG Pipeline

The application follows this pipeline:

```text
PDF
 |
 v
PyMuPDFLoader
 |
 v
RecursiveCharacterTextSplitter
 |
 v
HuggingFace Embeddings
 |
 v
Chroma Vector Database
 |
 v
Retriever
 |
 v
Marketing Retrieval Tool
 |
 v
Qwen LLM
 |
 v
Final Answer
```

---

## Design Documentation

For detailed information about:

* Design decisions
* Architecture
* Trade-offs
* Limitations
* Production scaling approach

see:

`DESIGN.md`
