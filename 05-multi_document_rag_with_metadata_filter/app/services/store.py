from dataclasses import dataclass
from math import sqrt
from typing import Any


@dataclass
class DocChunk:
    id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any]  # source_id, filename, source


_store: list[DocChunk] = []
_next_id: int = 0
_next_doc_id: int = 0


def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _matches(chunk: DocChunk, filt: dict[str, Any] | None) -> bool:
    if not filt:
        return True
    for k, v in filt.items():
        if chunk.metadata.get(k) != v:
            return False
    return True


def get_store() -> tuple[list[DocChunk], int, int]:
    global _store, _next_id, _next_doc_id
    return _store, _next_id, _next_doc_id


def clear_store() -> None:
    global _store, _next_id, _next_doc_id
    _store = []
    _next_id = 0
    _next_doc_id = 0


def next_doc_id() -> str:
    global _next_doc_id
    _next_doc_id += 1
    return f"doc{_next_doc_id}"


def add_chunks(chunks: list[tuple[str, list[float], dict[str, Any]]]) -> None:
    global _store, _next_id
    for text, emb, meta in chunks:
        _next_id += 1
        _store.append(DocChunk(id=f"c{_next_id}", text=text, embedding=emb, metadata=meta.copy()))


def search(
    query_embedding: list[float],
    top_k: int,
    metadata_filter: dict[str, Any] | None = None,
) -> list[tuple[DocChunk, float]]:
    global _store
    candidates = [c for c in _store if _matches(c, metadata_filter)]
    if not candidates:
        return []
    scored = [(_cosine_sim(query_embedding, c.embedding), c) for c in candidates]
    scored.sort(key=lambda x: -x[0])
    return scored[:top_k]
