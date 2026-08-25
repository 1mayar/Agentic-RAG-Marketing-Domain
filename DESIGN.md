# Design Document — Marketing Campaign Strategist Agent

## 1. Overview

The project implements a Retrieval-Augmented Generation (RAG) based Marketing Campaign Strategist Agent using LangChain.

The system uses a marketing book as the primary knowledge source. The PDF is loaded, split into smaller chunks, converted into vector embeddings, and stored in a Chroma vector database.

When a user asks a marketing-related question, the agent uses a LangChain retrieval tool to find relevant passages from the book. These passages are then provided to the LLM as context for generating the final answer.

The goal is to keep marketing answers grounded in the provided knowledge source while maintaining a simple and lightweight architecture.

---

# 2. Design Decisions

## 2.1 RAG Architecture

A Retrieval-Augmented Generation architecture was selected instead of relying only on the LLM's pretrained knowledge.

The marketing book is treated as the source of truth for marketing-related answers.

This provides two main benefits:

* The model can answer using the specific knowledge provided in the project.
* The system reduces the risk of unsupported or hallucinated marketing recommendations.

---

## 2.2 PDF Processing

`PyMuPDFLoader` is used to extract text from the marketing PDF.

The extracted document is then split using `RecursiveCharacterTextSplitter`.

The current configuration is:

* Chunk size: 1200 characters
* Chunk overlap: 250 characters

The overlap helps preserve context between adjacent chunks.

---

## 2.3 Embedding Model

The project uses:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

This model was selected because it provides multilingual semantic embeddings while remaining relatively lightweight.

Multilingual support is useful because users may interact with the agent in both Arabic and English.

---

## 2.4 Vector Database

Chroma is used as the vector database.

The vector store is persisted locally in:

`./chroma_db_marketing`

This means the PDF does not need to be re-embedded every time the application starts.

For a small prototype, local Chroma provides a simple and low-cost solution.

---

## 2.5 Retrieval Tool

The retriever is exposed as a LangChain tool:

`marketing_book_retriever`

The tool receives a query, performs semantic similarity search, and returns the top 8 relevant document chunks.

This separates document retrieval from the LLM and makes the retrieval functionality reusable.

---

## 2.6 LLM

The project uses:

`qwen/qwen-2.5-72b-instruct`

through OpenRouter.

The temperature is set to `0.0` to make the output more deterministic.

A relatively strong instruction-following model was selected because marketing strategy questions can require synthesis and reasoning across multiple retrieved passages.

---

## 2.7 Guardrails

The system prompt classifies queries into three categories:

### Greetings / Conversational

The agent responds naturally without retrieving information from the marketing book.

### Out-of-Domain / Safety Sensitive

Medical, diagnostic, financial, and non-marketing requests are refused without using the retrieval tool.

### Marketing

Marketing-related questions must use the marketing book retrieval tool before generating the answer.

This prevents unnecessary retrieval for irrelevant questions and provides a basic safety boundary around the application.

---

# 3. Trade-offs

## 3.1 Local Chroma vs. Managed Vector Database

### Local Chroma

Advantages:

* Simple setup
* No external database infrastructure
* Low cost
* Good for prototyping

Disadvantages:

* Not ideal for multiple application instances
* Limited scalability for very large datasets
* Requires shared storage or migration for distributed deployment

### Decision

Local Chroma is appropriate for the current prototype because the knowledge base is relatively small.

---

## 3.2 Lightweight Embeddings vs. Larger Embedding Models

The multilingual MiniLM embedding model is relatively lightweight.

Advantages:

* Lower computational requirements
* Faster local inference
* Multilingual support

Disadvantages:

* Retrieval quality may be lower than larger modern embedding models
* Domain-specific marketing concepts may not always be represented optimally

For production, multiple embedding models should be evaluated using a domain-specific retrieval benchmark.

---

## 3.3 Top-K = 8

The retriever currently returns 8 chunks.

A larger K can increase recall because more information is retrieved.

However, it also increases:

* Prompt size
* Token usage
* Latency
* Potential irrelevant context

A smaller K reduces cost and latency but can miss relevant information.

Therefore, 8 is used as a practical starting point and should be tuned through evaluation.

---

## 3.4 Large LLM vs. Smaller LLM

A larger instruction-following model can provide stronger reasoning and synthesis.

However, it may have:

* Higher latency
* Higher cost
* Higher resource requirements

For production, a smaller model could handle simple questions while a larger model could be reserved for complex marketing strategy queries.

---

# 4. Scaling Approach

The current implementation is designed as a prototype.

For production deployment, I would scale the system in the following way.

## 4.1 Separate Ingestion from Querying

Document ingestion should be separated from the user-facing application.

Instead of creating the vector database during application startup, an ingestion pipeline would process documents independently:

```text
Documents
    |
    v
Document Loader
    |
    v
Chunking
    |
    v
Embedding Generation
    |
    v
Vector Database
```

The online agent would then only perform retrieval and generation.

This reduces startup time and avoids unnecessary document processing.

---

## 4.2 Production Vector Database

For a larger knowledge base or multiple application instances, the local Chroma database could be replaced by a managed or server-based vector database.

This allows multiple agent instances to access the same knowledge base.

---

## 4.3 Metadata

Each chunk could contain metadata such as:

* Document name
* Page number
* Chapter
* Topic
* Document version

Metadata filtering would allow more precise retrieval.

For example, the system could retrieve only content from a specific chapter or document version.

---

## 4.4 Hybrid Retrieval and Re-ranking

A production retrieval pipeline could combine:

* Dense vector search
* Keyword search
* Metadata filtering
* Cross-encoder re-ranking

The first retrieval stage could retrieve a larger candidate set, followed by a re-ranker that selects the most relevant passages.

This can improve retrieval precision for specialized marketing terminology.

---

## 4.5 Caching

Frequently repeated queries could be cached.

Caching could reduce:

* Retrieval latency
* LLM calls
* Infrastructure cost

---

## 4.6 Monitoring and Evaluation

A production system should monitor:

* Retrieval latency
* LLM latency
* Token usage
* Error rate
* Retrieved document relevance
* User feedback
* Answer quality

A dedicated evaluation dataset should also be created containing representative marketing questions and expected relevant sections from the source documents.

---

# 5. Limitations

The current prototype has several limitations:

1. It uses a local vector database.
2. It is currently CLI-based.
3. It does not include authentication or user management.
4. It does not maintain long-term conversational memory.
5. Retrieval quality has not been formally benchmarked.
6. The system depends on the quality and coverage of the marketing book.
7. The retrieval workflow currently performs a single retrieval step.
8. The current implementation is not designed for high-concurrency production traffic.

These limitations are acceptable for a prototype and can be addressed as the system evolves.

---

# 6. Summary

The final solution uses a lightweight RAG architecture built with LangChain.

The system combines:

* PDF document processing
* Recursive chunking
* Multilingual embeddings
* Chroma vector storage
* Tool-based retrieval
* Qwen 2.5 72B
* Domain guardrails

The architecture prioritizes simplicity, multilingual support, low infrastructure requirements, and grounding responses in the provided marketing knowledge source.

For production scaling, the main improvements would be separating ingestion from querying, introducing a production-grade vector database, improving retrieval through hybrid search and re-ranking, adding caching, and implementing monitoring and evaluation.
