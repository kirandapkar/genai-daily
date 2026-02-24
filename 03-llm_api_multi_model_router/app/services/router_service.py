import logging
import time
from dataclasses import dataclass

from app.config import get_settings
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass
class RouterResult:
    text: str
    provider: str
    model: str
    latency_ms: float
    fallback_used: bool


def router_service(prompt: str, llm: LLMService | None = None) -> RouterResult:
    settings = get_settings()
    if llm is None:
        llm = LLMService()
    chain = [p.strip().lower() for p in settings.router_chain.split(",") if p.strip()]
    max_latency = settings.max_latency_ms
    last_err: Exception | None = None

    for i, provider in enumerate(chain):
        try:
            start = time.perf_counter()
            if provider == "gemini":
                text = llm.complete_gemini(prompt, None)
            elif provider == "openrouter":
                text = llm.complete_openrouter(prompt, None)
            else:
                logger.warning("unknown_provider", extra={"provider": provider})
                continue
            latency_ms = (time.perf_counter() - start) * 1000
            model = settings.default_gemini_model if provider == "gemini" else settings.default_openrouter_model
            if max_latency > 0 and latency_ms > max_latency:
                logger.info("latency_exceeded", extra={"provider": provider, "latency_ms": latency_ms})
                last_err = TimeoutError(f"Latency {latency_ms:.0f}ms > {max_latency}ms")
                continue
            return RouterResult(
                text=text,
                provider=provider,
                model=model,
                latency_ms=round(latency_ms, 2),
                fallback_used=i > 0,
            )
        except Exception as e:
            last_err = e
            logger.warning("router_fallback", extra={"provider": provider, "error": str(e)})
    if last_err is not None:
        raise last_err
    raise RuntimeError("No providers in router chain")
