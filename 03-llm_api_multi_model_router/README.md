# 03 – LLM API Multi-Model Router

Automatic fallback between models based on **failure** or **latency**.

## Features

- **Provider chain:** Try providers in order (e.g. `gemini` then `openrouter`). On success return; on failure or slow response try next.
- **Latency threshold:** Optional `MAX_LATENCY_MS`; if response is slower, router tries the next provider.
- **Response:** `text`, `provider`, `model`, `latency_ms`, `fallback_used`.

## Config

- `ROUTER_CHAIN` – comma-separated providers, e.g. `gemini,openrouter`
- `MAX_LATENCY_MS` – optional; 0 = no latency-based fallback

## Setup

```bash
cp .env.example .env
# Add OPENROUTER_API_KEY and GEMINI_API_KEY
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --port 8000
```

## Example

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello."}'
```

## Tests

```bash
pytest -v
```
