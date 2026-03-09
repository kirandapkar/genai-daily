from typing import Any

from app.config import get_settings

_model: Any = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        s = get_settings()
        _model = SentenceTransformer(s.embedding_model)
    return _model


def embedding_service(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    emb = model.encode(texts)
    return emb.tolist() if hasattr(emb, "tolist") else list(emb)
