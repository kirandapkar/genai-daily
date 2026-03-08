from dataclasses import dataclass, field
from math import sqrt


@dataclass
class DocChunk:
    id: str
    text: str
    embedding: list[float]


_store: list[DocChunk] = []
_next_id: int = 0


def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def get_store() -> tuple[list[DocChunk], int]:
    global _store, _next_id
    return _store, _next_id


def clear_store() -> None:
    global _store, _next_id
    _store = []
    _next_id = 0


def add_chunks(chunks: list[tuple[str, list[float]]]) -> None:
    global _store
    global _next_id
    for text, emb in chunks:
        _next_id += 1
        _store.append(DocChunk(id=f"c{_next_id}", text=text, embedding=emb))


def search(query_embedding: list[float], top_k: int) -> list[tuple[DocChunk, float]]:
    global _store
    if not _store:
        return []
    scored = [(_cosine_sim(query_embedding, c.embedding), c) for c in _store]
    scored.sort(key=lambda x: -x[0])
    return scored[:top_k]
