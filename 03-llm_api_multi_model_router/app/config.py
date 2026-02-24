import os
from pydantic import BaseModel


class Settings(BaseModel):
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_openrouter_model: str = "openrouter/free"
    default_gemini_model: str = "gemini-3-flash-preview"
    max_retries: int = 3
    request_timeout: float = 60.0
    max_latency_ms: float = 0.0  # 0 = no latency-based fallback
    router_chain: str = "gemini,openrouter"  # comma-separated providers


def get_settings() -> Settings:
    chain = os.getenv("ROUTER_CHAIN", "gemini,openrouter").strip()
    return Settings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        max_latency_ms=float(os.getenv("MAX_LATENCY_MS", "0")),
        router_chain=chain,
    )
