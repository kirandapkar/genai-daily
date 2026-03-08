from unittest.mock import patch

from app.services.rag_service import rag_ingest, rag_ask, AskResult


def test_rag_ingest_empty_pdf_returns_zero() -> None:
    # PDF with no extractable text
    empty_pdf = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n"
    with patch("app.services.rag_service.extract_text_from_pdf", return_value=""):
        n = rag_ingest(empty_pdf)
    assert n == 0


def test_rag_ingest_with_mocked_extract_and_embed() -> None:
    with patch("app.services.rag_service.extract_text_from_pdf", return_value="Hello world. " * 50):
        with patch("app.services.rag_service.chunk_text", return_value=["chunk1", "chunk2"]):
            with patch("app.services.rag_service.embedding_service", return_value=[[0.1] * 384, [0.1] * 384]):
                n = rag_ingest(b"fake pdf")
    assert n == 2


def test_rag_ask_no_doc_returns_message() -> None:
    from app.services.store import clear_store
    clear_store()
    with patch("app.services.rag_service.embedding_service", return_value=[[0.1] * 384]):
        r = rag_ask("What is this?")
    assert "No document" in r.answer
    assert r.citations == []


def test_rag_ask_with_context_calls_gemini() -> None:
    from app.services.store import DocChunk
    result_val = [(0.9, DocChunk(id="c1", text="Some context.", embedding=[]))]
    with patch("app.services.rag_service.embedding_service", return_value=[[0.1] * 384]):
        with patch("app.services.rag_service.search", return_value=result_val):
            with patch("app.services.rag_service._call_gemini", return_value="The answer."):
                r = rag_ask("What?")
    assert r.answer == "The answer."
    assert r.citations == ["Some context."]
