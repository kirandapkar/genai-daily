# 04 – Single-Document RAG System

PDF ingestion, embedding, vector search, and citation answers.

## Features

- **Ingest:** Upload a PDF → extract text → chunk → embed (sentence-transformers) → store in memory.
- **Ask:** Ask a question → vector search → top-k chunks → LLM (Gemini) with context → answer + citations.

## API

- `POST /v1/ingest` – form file upload (PDF). Returns `{ "status": "ok", "chunks_ingested": N }`.
- `POST /v1/ask` – body `{ "question": "..." }`. Returns `{ "answer": "...", "citations": ["..."] }`.

## Setup

```bash
cp .env.example .env
# Add GEMINI_API_KEY
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --port 8000
```

## Example

```bash
curl -X POST http://localhost:8000/v1/ingest -F "file=@doc.pdf"
curl -X POST http://localhost:8000/v1/ask -H "Content-Type: application/json" -d '{"question": "What is the main topic?"}'
```

## Tests

```bash
pytest -v
```
