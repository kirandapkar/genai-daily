import logging
import time
import uuid
from typing import Any

import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def _log_request(self, model: str, latency_ms: float, extra: dict[str, Any] | None = None) -> None:
        log_extra = {"model": model, "latency_ms": round(latency_ms, 2), **(extra or {})}
        logger.info("llm_request", extra=log_extra)

    def complete_openrouter(self, prompt: str, model: str | None = None) -> str:
        if not self._settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
        model = model or self._settings.default_openrouter_model
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()
        last_err: Exception | None = None
        for attempt in range(1, self._settings.max_retries + 1):
            try:
                with httpx.Client(timeout=self._settings.request_timeout) as client:
                    r = client.post(
                        f"{self._settings.openrouter_base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                        },
                    )
                    r.raise_for_status()
                    data = r.json()
                    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    latency_ms = (time.perf_counter() - start) * 1000
                    self._log_request(model, latency_ms, {"request_id": request_id})
                    return text.strip()
            except Exception as e:
                last_err = e
                logger.warning("openrouter_attempt_failed", extra={"attempt": attempt, "error": str(e)})
        latency_ms = (time.perf_counter() - start) * 1000
        self._log_request(model, latency_ms, {"request_id": request_id, "error": str(last_err)})
        raise last_err  # type: ignore

    def complete_gemini(self, prompt: str, model: str | None = None) -> str:
        if not self._settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        try:
            from google import genai
        except ImportError:
            raise ImportError("Install google-genai: pip install google-genai")
        model = model or self._settings.default_gemini_model
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()
        last_err: Exception | None = None
        for attempt in range(1, self._settings.max_retries + 1):
            try:
                client = genai.Client(api_key=self._settings.gemini_api_key)
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                text = (response.text or "").strip()
                latency_ms = (time.perf_counter() - start) * 1000
                self._log_request(model, latency_ms, {"request_id": request_id})
                return text
            except Exception as e:
                last_err = e
                logger.warning("gemini_attempt_failed", extra={"attempt": attempt, "error": str(e)})
        raise last_err  # type: ignore
