from app.services.store import add_chunks, clear_store, search


def test_search_with_metadata_filter() -> None:
    clear_store()
    emb = [0.1] * 384
    add_chunks([
        ("chunk A", emb, {"source_id": "doc1", "source": "a.pdf"}),
        ("chunk B", emb, {"source_id": "doc2", "source": "b.pdf"}),
    ])
    q = [0.11] * 384
    all_res = search(q, 5, None)
    assert len(all_res) == 2
    filtered = search(q, 5, {"source_id": "doc1"})
    assert len(filtered) == 1
    assert filtered[0][1].text == "chunk A"
    assert filtered[0][1].metadata["source_id"] == "doc1"


def test_search_empty_with_filter() -> None:
    clear_store()
    assert search([0.1] * 384, 5, {"source_id": "doc1"}) == []
