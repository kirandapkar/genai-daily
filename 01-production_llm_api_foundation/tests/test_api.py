from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import chat


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_chat_requires_valid_provider(client: TestClient) -> None:
    r = client.post(
        "/v1/chat",
        json={"prompt": "hi", "provider": "invalid"},
    )
    assert r.status_code == 422


def test_chat_openrouter_missing_key_returns_500(client: TestClient) -> None:
    chat._service = None  # reset cached service so it uses patched env
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "", "GEMINI_API_KEY": ""}, clear=False):
        r = client.post(
            "/v1/chat",
            json={"prompt": "hi", "provider": "openrouter"},
        )
        assert r.status_code in (500, 422)
