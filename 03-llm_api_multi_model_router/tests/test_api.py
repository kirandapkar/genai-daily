from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_chat_returns_200_with_mocked_router() -> None:
    from app.services.router_service import RouterResult
    with patch("app.routers.chat.router_service") as mock_router:
        mock_router.return_value = RouterResult(
            text="Hello",
            provider="gemini",
            model="gemini-3-flash-preview",
            latency_ms=100.0,
            fallback_used=False,
        )
        r = client.post("/v1/chat", json={"prompt": "hi"})
        assert r.status_code == 200
        j = r.json()
        assert j["text"] == "Hello"
        assert j["provider"] == "gemini"
        assert j["latency_ms"] == 100.0
        assert j["fallback_used"] is False


def test_chat_returns_503_when_router_raises() -> None:
    with patch("app.routers.chat.router_service") as mock_router:
        mock_router.side_effect = RuntimeError("all failed")
        r = client.post("/v1/chat", json={"prompt": "hi"})
        assert r.status_code == 503
