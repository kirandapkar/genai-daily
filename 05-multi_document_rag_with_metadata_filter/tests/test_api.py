from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ingest_requires_pdf() -> None:
    r = client.post("/v1/ingest", files={"file": ("x.txt", b"data", "text/plain")})
    assert r.status_code == 400


def test_ingest_returns_doc_id() -> None:
    with patch("app.routers.rag.rag_ingest") as m:
        m.return_value = type("R", (), {"doc_id": "doc1", "chunks_ingested": 3})()
        r = client.post("/v1/ingest", files={"file": ("a.pdf", b"fake", "application/pdf")})
    assert r.status_code == 200
    assert "doc_id" in r.json()
    assert r.json()["chunks_ingested"] == 3


def test_ask_with_filter() -> None:
    from app.services.rag_service import AskResult
    with patch("app.routers.rag.rag_ask") as m:
        m.return_value = AskResult(answer="Yes.", citations=[])
        r = client.post("/v1/ask", json={"question": "What?", "metadata_filter": {"source_id": "doc1"}})
    assert r.status_code == 200
    assert r.json()["answer"] == "Yes."
