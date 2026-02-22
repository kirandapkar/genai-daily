from app.services.metrics import estimate_cost, estimate_tokens


def test_estimate_tokens() -> None:
    assert estimate_tokens("") == 1
    assert estimate_tokens("hi") == 1
    assert estimate_tokens("a" * 4) == 1
    assert estimate_tokens("a" * 5) == 2


def test_estimate_cost() -> None:
    c = estimate_cost(1000, 500, 0.001, 0.002)
    assert abs(c - (1.0 * 0.001 + 0.5 * 0.002)) < 0.0001
