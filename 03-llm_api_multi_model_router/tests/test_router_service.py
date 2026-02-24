import os
from unittest.mock import MagicMock, patch

import pytest

from app.services.router_service import RouterResult, router_service


def test_router_returns_primary_when_success() -> None:
    mock_llm = MagicMock()
    mock_llm.complete_gemini.return_value = "Hi"
    with patch.dict(os.environ, {"ROUTER_CHAIN": "gemini,openrouter", "GEMINI_API_KEY": "x", "OPENROUTER_API_KEY": "y"}, clear=False):
        result = router_service("hello", llm=mock_llm)
    assert result.text == "Hi"
    assert result.provider == "gemini"
    assert result.fallback_used is False
    mock_llm.complete_gemini.assert_called_once()
    mock_llm.complete_openrouter.assert_not_called()


def test_router_fallback_on_primary_failure() -> None:
    mock_llm = MagicMock()
    mock_llm.complete_gemini.side_effect = RuntimeError("fail")
    mock_llm.complete_openrouter.return_value = "From OpenRouter"
    with patch.dict(os.environ, {"ROUTER_CHAIN": "gemini,openrouter", "GEMINI_API_KEY": "x", "OPENROUTER_API_KEY": "y"}, clear=False):
        result = router_service("hello", llm=mock_llm)
    assert result.text == "From OpenRouter"
    assert result.provider == "openrouter"
    assert result.fallback_used is True
    mock_llm.complete_gemini.assert_called_once()
    mock_llm.complete_openrouter.assert_called_once()


def test_router_fallback_on_latency_exceeded() -> None:
    mock_llm = MagicMock()
    mock_llm.complete_gemini.return_value = "Slow"
    with patch.dict(os.environ, {"ROUTER_CHAIN": "gemini,openrouter", "MAX_LATENCY_MS": "1", "GEMINI_API_KEY": "x", "OPENROUTER_API_KEY": "y"}, clear=False):
        with patch("app.services.router_service.time.perf_counter", side_effect=[0.0, 0.1, 0.0, 0.001]):
            mock_llm.complete_openrouter.return_value = "Fast"
            result = router_service("hello", llm=mock_llm)
    assert result.text == "Fast"
    assert result.provider == "openrouter"
    assert result.fallback_used is True


def test_router_raises_when_all_fail() -> None:
    mock_llm = MagicMock()
    mock_llm.complete_gemini.side_effect = RuntimeError("gemini fail")
    mock_llm.complete_openrouter.side_effect = RuntimeError("openrouter fail")
    with patch.dict(os.environ, {"ROUTER_CHAIN": "gemini,openrouter", "GEMINI_API_KEY": "x", "OPENROUTER_API_KEY": "y"}, clear=False):
        with pytest.raises(RuntimeError, match="openrouter fail"):
            router_service("hello", llm=mock_llm)


def test_router_skips_unknown_provider() -> None:
    mock_llm = MagicMock()
    mock_llm.complete_openrouter.return_value = "OK"
    with patch.dict(os.environ, {"ROUTER_CHAIN": "unknown,openrouter", "GEMINI_API_KEY": "x", "OPENROUTER_API_KEY": "y"}, clear=False):
        result = router_service("hello", llm=mock_llm)
    assert result.text == "OK"
    assert result.provider == "openrouter"
