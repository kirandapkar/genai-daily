# Design: Production LLM API Foundation

## Goal

FastAPI service that wraps multi-model LLM calls with retries and logging. Supports OpenRouter (free models) and Gemini.

## Architecture

- **API layer:** FastAPI; single `/v1/chat` (or `/generate`) endpoint; Pydantic request/response.
- **Service layer:** `LLMService` in `app/services/llm_service.py` – no business logic in routes.
- **Providers:** OpenRouter (OpenAI-compatible API), Gemini (`google-genai` SDK).
- **Resilience:** Configurable retries with backoff; structured logging (request id, model, latency, token usage).
- **Config:** `OPENROUTER_API_KEY`, `GEMINI_API_KEY` from env; model names configurable.

## Data

- Use real models: OpenRouter free tier (e.g. `openrouter/google/gemma-2-9b-it:free`) and/or Gemini.
- No fake data: responses come from live API calls.

## Structure

```
app/
  main.py          # FastAPI app, lifespan
  config.py        # settings from env
  services/
    llm_service.py # openrouter + gemini, retries, logging
  routers/
    chat.py        # POST /v1/chat
tests/
  test_llm_service.py  # mock HTTP / mock client
  test_api.py          # TestClient, optional live key
```

## Acceptance

- Unit tests pass (mocked provider).
- One command runs the app (e.g. `uvicorn app.main:app`).
- README: architecture, setup, example curl.
- No hardcoded secrets.
