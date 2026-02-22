from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import chat

client = TestClient(app, raise_server_exceptions=False)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_chat_invalid_provider() -> None:
    r = client.post("/v1/chat", json={"prompt": "hi", "provider": "invalid"})
    assert r.status_code == 422


def test_rate_limit_returns_429() -> None:
    chat._limiter = None
    with patch("app.routers.chat.get_limiter") as mock:
        from app.services.rate_limit import RateLimiter
        limiter = RateLimiter(max_requests=1, window_sec=60)
        mock.return_value = limiter
        chat._service = None
        with patch("app.services.llm_service.LLMService.complete_gemini", return_value="Hi"):
            with patch.dict("os.environ", {"GEMINI_API_KEY": "x", "OPENROUTER_API_KEY": ""}, clear=False):
                r1 = client.post("/v1/chat", json={"prompt": "hi", "provider": "gemini"}, headers={"X-Api-Key": "rl-test"})
                assert r1.status_code == 200
                r2 = client.post("/v1/chat", json={"prompt": "hi", "provider": "gemini"}, headers={"X-Api-Key": "rl-test"})
                assert r2.status_code == 429
                assert "Retry-After" in r2.headers


def test_chat_returns_tokens_and_cost() -> None:
    chat._limiter = None
    chat._service = None
    with patch("app.routers.chat.get_limiter") as mock_limiter:
        from app.services.rate_limit import RateLimiter
        mock_limiter.return_value = RateLimiter(max_requests=100, window_sec=60)
    with patch("app.services.llm_service.LLMService.complete_gemini", return_value="Hello"):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "x", "OPENROUTER_API_KEY": ""}, clear=False):
            r = client.post("/v1/chat", json={"prompt": "hi", "provider": "gemini"}, headers={"X-Api-Key": "cost-test"})
            assert r.status_code == 200
            j = r.json()
            assert "tokens_in" in j
            assert "tokens_out" in j
            assert "cost_estimated" in j
            assert "rate" in j
            assert j["text"] == "Hello"
