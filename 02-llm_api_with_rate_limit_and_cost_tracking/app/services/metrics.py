import math


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def estimate_cost(
    tokens_in: int, tokens_out: int, cost_per_1k_in: float, cost_per_1k_out: float
) -> float:
    return (tokens_in / 1000 * cost_per_1k_in) + (tokens_out / 1000 * cost_per_1k_out)
