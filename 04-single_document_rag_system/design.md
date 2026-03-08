# Design: Single-Document RAG System

PDF ingestion, embedding, vector search, and citation answers.

## Flow

1. **Ingest:** Upload PDF → extract text (pypdf) → chunk (fixed size + overlap) → embed (sentence-transformers all-MiniLM-L6-v2) → store in memory.
2. **Ask:** Question → embed query → vector search (cosine similarity) → top-k chunks → LLM (Gemini) with context → answer + citation chunks.

## Components

- **pdf_service:** Extract text from PDF bytes.
- **chunk_service:** Split text into chunks (e.g. 400 chars, 50 overlap).
- **embedding_service:** Load model, embed list of texts.
- **store:** In-memory list of (embedding, text, id); search by cosine similarity.
- **rag_service:** ingest(pdf_bytes); ask(question) → answer + citations.
- **API:** POST /ingest (file), POST /ask ({"question": "..."}).

## Config

GEMINI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K.
