from unittest.mock import patch

from app.services.rag_service import rag_ingest, rag_ask, IngestResult
from app.services.store import clear_store


def test_rag_ingest_returns_doc_id_and_count() -> None:
    clear_store()
    with patch("app.services.rag_service.extract_text_from_pdf", return_value="x " * 100):
        with patch("app.services.rag_service.chunk_text", return_value=["c1", "c2"]):
            with patch("app.services.rag_service.embedding_service", return_value=[[0.1] * 384, [0.1] * 384]):
                r = rag_ingest(b"pdf")
    assert isinstance(r, IngestResult)
    assert r.doc_id.startswith("doc")
    assert r.chunks_ingested == 2


def test_rag_ask_no_doc() -> None:
    clear_store()
    with patch("app.services.rag_service.embedding_service", return_value=[[0.1] * 384]):
        r = rag_ask("What?")
    assert "No matching" in r.answer or "ask a question" in r.answer.lower()
    assert r.citations == []


def test_rag_ask_with_filter_and_mocked_llm() -> None:
    from app.services.store import DocChunk
    result_val = [(0.9, DocChunk(id="c1", text="Context.", embedding=[], metadata={}))]
    with patch("app.services.rag_service.embedding_service", return_value=[[0.1] * 384]):
        with patch("app.services.rag_service.search", return_value=result_val):
            with patch("app.services.rag_service._call_gemini", return_value="Answer."):
                r = rag_ask("What?", metadata_filter={"source_id": "doc1"})
    assert r.answer == "Answer."
    assert r.citations == ["Context."]
