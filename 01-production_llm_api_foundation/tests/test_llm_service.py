import os
from unittest.mock import patch

import pytest
from app.config import get_settings
from app.services import LLMService


def test_get_settings_loads_env() -> None:
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test", "GEMINI_API_KEY": "key-test"}):
        s = get_settings()
        assert s.openrouter_api_key == "sk-test"
        assert s.gemini_api_key == "key-test"


def test_openrouter_raises_without_key() -> None:
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "", "GEMINI_API_KEY": ""}, clear=False):
        svc = LLMService()
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            svc.complete_openrouter("hello")


def test_gemini_raises_without_key() -> None:
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "", "GEMINI_API_KEY": ""}, clear=False):
        svc = LLMService()
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            svc.complete_gemini("hello")


def test_openrouter_success_mocked(httpx_mock: pytest.fixture) -> None:
    httpx_mock.add_response(
        json={
            "choices": [{"message": {"content": "Hi there"}}],
        },
    )
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test", "GEMINI_API_KEY": ""}, clear=False):
        svc = LLMService()
        out = svc.complete_openrouter("hi")
        assert out == "Hi there"
