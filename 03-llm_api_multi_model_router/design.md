# Design: LLM API Multi-Model Router

Automatic fallback between models based on **failure** or **latency**.

## Behavior

- **Provider chain:** Try providers in order (e.g. Gemini → OpenRouter). On success and latency ≤ `max_latency_ms`, return. On failure or slow response, try next.
- **Response:** Include `text`, `provider`, `model`, `latency_ms`, `fallback_used` (true if primary failed/slow).
- **Config:** `router_chain` = list of `provider[:model]` (e.g. `gemini`, `openrouter`), `max_latency_ms` (optional; 0 = no latency check).

## Structure

- `app/config.py` – settings + router chain + max_latency_ms
- `app/services/llm_service.py` – same as day2 (Gemini + OpenRouter)
- `app/services/router_service.py` – try chain, respect latency, return first success
- `app/routers/chat.py` – POST /v1/chat, uses router
- `app/main.py` – FastAPI app

## Tests

- Router: returns primary result when primary succeeds and fast
- Router: on primary failure, returns fallback result
- Router: on primary slow (latency > threshold), tries fallback and returns fallback result
- Router: when all fail, raises
- API: health, chat returns 200 with provider/latency/fallback_used
