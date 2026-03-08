from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ingest_requires_pdf() -> None:
    r = client.post("/v1/ingest", files={"file": ("x.txt", b"not a pdf", "text/plain")})
    assert r.status_code == 400


def test_ask_returns_answer_and_citations() -> None:
    from app.services.rag_service import AskResult
    with patch("app.routers.rag.rag_ask") as m:
        m.return_value = AskResult(answer="No document.", citations=[])
        r = client.post("/v1/ask", json={"question": "What?"})
    assert r.status_code == 200
    j = r.json()
    assert "answer" in j
    assert "citations" in j
