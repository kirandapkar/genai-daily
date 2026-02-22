# 02 – LLM API with Rate Limit & Cost Tracking

Extends day1 with per-API-key rate limiting, token estimation, and cost tracking.

## Features

- Rate limiting (in-memory, per `X-Api-Key` header)
- Token estimation (~4 chars/token)
- Cost estimation per request
- Response includes `tokens_in`, `tokens_out`, `cost_estimated`, `rate.remaining`

## Setup

```bash
cp .env.example .env
# Add OPENROUTER_API_KEY and/or GEMINI_API_KEY
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
  -H "X-Api-Key: my-key" \
  -d '{"prompt": "Say hi.", "provider": "gemini"}'
```

## Tests

```bash
pytest -v
```
