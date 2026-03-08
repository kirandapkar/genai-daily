import logging
import os
from dataclasses import dataclass

from app.config import get_settings
from app.services.chunk_service import chunk_text
from app.services.embedding_service import embedding_service
from app.services.pdf_service import extract_text_from_pdf
from app.services.store import add_chunks, clear_store, search

logger = logging.getLogger(__name__)


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


def rag_ingest(pdf_bytes: bytes) -> int:
    clear_store()
    text = extract_text_from_pdf(pdf_bytes)
    if not text:
        return 0
    chunks = chunk_text(text)
    if not chunks:
        return 0
    embeddings = embedding_service(chunks)
    add_chunks(list(zip(chunks, embeddings)))
    return len(chunks)


def rag_ask(question: str) -> AskResult:
    settings = get_settings()
    if not question.strip():
        return AskResult(answer="Please ask a question.", citations=[])
    query_emb = embedding_service([question])[0]
    results = search(query_emb, settings.top_k)
    if not results:
        return AskResult(
            answer="No document has been ingested yet. Upload a PDF first.",
            citations=[],
        )
    context = "\n\n---\n\n".join(f"[{c.id}] {c.text}" for _, c in results)
    citations = [c.text for _, c in results]
    prompt = f"""Use the following context to answer the question. Cite the source by referring to the chunk id in brackets.

Context:
{context}

Question: {question}

Answer (include [cN] citations where relevant):"""
    answer = _call_gemini(prompt)
    return AskResult(answer=answer, citations=citations)
