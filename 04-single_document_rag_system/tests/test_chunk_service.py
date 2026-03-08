from unittest.mock import patch

from app.services.chunk_service import chunk_text


def test_chunk_text_empty() -> None:
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_small() -> None:
    with patch("app.services.chunk_service.get_settings") as m:
        m.return_value = type("S", (), {"chunk_size": 400, "chunk_overlap": 50})()
        out = chunk_text("Hello world.")
        assert len(out) >= 1
        assert "Hello" in out[0]


def test_chunk_text_splits_large() -> None:
    with patch("app.services.chunk_service.get_settings") as m:
        m.return_value = type("S", (), {"chunk_size": 10, "chunk_overlap": 2})()
        out = chunk_text("a" * 30)
        assert len(out) >= 2
