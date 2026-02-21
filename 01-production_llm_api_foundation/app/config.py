import os
from pydantic import BaseModel


class Settings(BaseModel):
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_openrouter_model: str = "openrouter/google/gemma-2-9b-it:free"
    default_gemini_model: str = "gemini-2.0-flash"
    max_retries: int = 3
    request_timeout: float = 60.0


def get_settings() -> Settings:
    return Settings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
    )
