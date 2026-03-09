# Design: Multi-Document RAG with Metadata Filter

Extend single-doc RAG: ingest multiple PDFs, attach metadata (source_id, filename, source), filter by metadata at query time. Hybrid retrieval = vector search + metadata filter.

## Components

- **Store:** Chunks have metadata (source_id, filename, source). search(query_emb, top_k, metadata_filter dict).
- **Ingest:** POST one PDF at a time with optional metadata; append to store (no clear). Each ingest returns doc_id.
- **Ask:** Optional filter in body e.g. {"source_id": "doc1"} or {"source": "report.pdf"}; only chunks matching filter are searched.
- **API:** POST /v1/ingest (file + optional source, filename), POST /v1/ask (question, optional metadata_filter).
