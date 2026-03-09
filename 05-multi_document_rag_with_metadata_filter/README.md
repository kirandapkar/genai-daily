# 05 – Multi-Document RAG with Metadata Filter

Multi-doc ingestion: each PDF gets a doc_id and metadata (source, filename). Query with optional metadata filter for hybrid retrieval (vector + filter).

## API

- `POST /v1/ingest` – form: `file` (PDF), optional `source`, `filename`. Returns `doc_id`, `chunks_ingested`. Appends to store.
- `POST /v1/ask` – body: `{ "question": "...", "metadata_filter": { "source_id": "doc1" } }`. Filter is optional.

## Run

```bash
cp .env.example .env  # set GEMINI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

## Tests

```bash
pytest -v
```
