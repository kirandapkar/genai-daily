import logging
import os
from dataclasses import dataclass

from app.config import get_settings
from app.services.chunk_service import chunk_text
from app.services.embedding_service import embedding_service
from app.services.pdf_service import extract_text_from_pdf
from app.services.store import add_chunks, next_doc_id, search

logger = logging.getLogger(__name__)


@dataclass
class IngestResult:
    doc_id: str
    chunks_ingested: int


@dataclass
class AskResult:
    answer: str
    citations: list[str]


def _call_gemini(prompt: str) -> str:
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise ValueError("GEMINI_API_KEY is not set")
    from google import genai
    client = genai.Client(api_key=key)
    r = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return (r.text or "").strip()


def rag_ingest(
    pdf_bytes: bytes,
    source: str = "",
    filename: str = "",
) -> IngestResult:
    doc_id = next_doc_id()
    meta = {"source_id": doc_id, "source": source or doc_id, "filename": filename or "unknown"}
    text = extract_text_from_pdf(pdf_bytes)
    if not text:
        return IngestResult(doc_id=doc_id, chunks_ingested=0)
    chunks = chunk_text(text)
    if not chunks:
        return IngestResult(doc_id=doc_id, chunks_ingested=0)
    embeddings = embedding_service(chunks)
    add_chunks([(t, e, meta) for t, e in zip(chunks, embeddings)])
    return IngestResult(doc_id=doc_id, chunks_ingested=len(chunks))


def rag_ask(
    question: str,
    metadata_filter: dict[str, str] | None = None,
) -> AskResult:
    settings = get_settings()
    if not question.strip():
        return AskResult(answer="Please ask a question.", citations=[])
    query_emb = embedding_service([question])[0]
    results = search(query_emb, settings.top_k, metadata_filter=metadata_filter)
    if not results:
        return AskResult(
            answer="No matching documents. Ingest PDFs or try without a filter.",
            citations=[],
        )
    context = "\n\n---\n\n".join(f"[{c.id}] {c.text}" for _, c in results)
    citations = [c.text for _, c in results]
    prompt = f"""Use the following context to answer the question. Cite by chunk id in brackets.

Context:
{context}

Question: {question}

Answer (include [cN] where relevant):"""
    answer = _call_gemini(prompt)
    return AskResult(answer=answer, citations=citations)
