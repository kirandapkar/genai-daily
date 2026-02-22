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
    rate_limit_requests: int = 60
    rate_limit_window_sec: int = 60
    cost_per_1k_input: float = 0.0001
    cost_per_1k_output: float = 0.0002


def get_settings() -> Settings:
    return Settings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "60")),
        rate_limit_window_sec=int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60")),
    )
