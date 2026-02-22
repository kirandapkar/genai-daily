from app.services.rate_limit import RateLimiter


def test_rate_limiter_allows_within_limit() -> None:
    rl = RateLimiter(max_requests=2, window_sec=60)
    allowed, rem, _ = rl.check("key1")
    assert allowed is True
    assert rem == 1
    allowed, rem, _ = rl.check("key1")
    assert allowed is True
    assert rem == 0
    allowed, rem, retry = rl.check("key1")
    assert allowed is False
    assert rem == 0
    assert retry >= 0


def test_rate_limiter_per_key() -> None:
    rl = RateLimiter(max_requests=1, window_sec=60)
    allowed, _, _ = rl.check("a")
    assert allowed is True
    allowed, _, _ = rl.check("a")
    assert allowed is False
    allowed, _, _ = rl.check("b")
    assert allowed is True
