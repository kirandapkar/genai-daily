from app.services.store import add_chunks, clear_store, search


def test_add_and_search() -> None:
    clear_store()
    # Same-dim embeddings (e.g. 384 for MiniLM)
    emb1 = [0.1] * 384
    emb2 = [0.2] * 384
    add_chunks([("chunk one", emb1), ("chunk two", emb2)])
    # Query similar to emb1
    q = [0.11] * 384
    results = search(q, 2)
    assert len(results) == 2
    assert results[0][1].text in ("chunk one", "chunk two")


def test_search_empty_returns_empty() -> None:
    clear_store()
    assert search([0.1] * 384, 5) == []
