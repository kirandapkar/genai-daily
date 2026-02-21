# 01 – Production LLM API Foundation

FastAPI service wrapping multi-model LLM calls (OpenRouter + Gemini) with retries and logging.

## Architecture

- **API:** `POST /v1/chat` – body: `{ "prompt": "...", "provider": "openrouter"|"gemini", "model": null|"..." }`.
- **Service:** `app/services/llm_service.py` – OpenRouter (HTTP), Gemini (google-genai SDK); retries and structured logging.
- **Config:** Env vars only; no hardcoded secrets.

## Setup

```bash
cp .env.example .env
# Add OPENROUTER_API_KEY and/or GEMINI_API_KEY
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## Example

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain AI in one sentence.", "provider": "openrouter"}'
```

## Tests

```bash
pytest -v
```
