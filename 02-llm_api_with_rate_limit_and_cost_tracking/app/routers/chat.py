from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.config import get_settings
from app.services import LLMService, RateLimiter, estimate_cost, estimate_tokens

router = APIRouter(prefix="/v1", tags=["chat"])
_service: LLMService | None = None
_limiter: RateLimiter | None = None


def get_llm_service() -> LLMService:
    global _service
    if _service is None:
        _service = LLMService()
    return _service


def get_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        s = get_settings()
        _limiter = RateLimiter(s.rate_limit_requests, s.rate_limit_window_sec)
    return _limiter


class ChatRequest(BaseModel):
    prompt: str
    provider: str = "gemini"
    model: str | None = None


class RateInfo(BaseModel):
    limit: int
    window_seconds: int
    remaining: int


class ChatResponse(BaseModel):
    text: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_estimated: float
    rate: RateInfo


@router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    x_api_key: Annotated[str | None, Header(alias="X-Api-Key")] = None,
) -> ChatResponse:
    key = (x_api_key or "anonymous").strip() or "anonymous"
    settings = get_settings()
    limiter = get_limiter()
    allowed, remaining, retry_after = limiter.check(key)
    if not allowed:
        raise HTTPException(
            429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )
    svc = get_llm_service()
    model = req.model or (
        settings.default_gemini_model if req.provider == "gemini" else settings.default_openrouter_model
    )
    try:
        if req.provider == "gemini":
            text = svc.complete_gemini(req.prompt, model)
        elif req.provider == "openrouter":
            text = svc.complete_openrouter(req.prompt, model)
        else:
            raise HTTPException(422, detail="provider must be gemini or openrouter")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(503, detail=str(e))
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
            raise HTTPException(503, detail="Provider rate limit or quota exceeded.")
        raise HTTPException(503, detail=str(e))
    tokens_in = estimate_tokens(req.prompt)
    tokens_out = estimate_tokens(text)
    cost = estimate_cost(
        tokens_in, tokens_out,
        settings.cost_per_1k_input, settings.cost_per_1k_output,
    )
    return ChatResponse(
        text=text,
        provider=req.provider,
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_estimated=round(cost, 6),
        rate=RateInfo(
            limit=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_sec,
            remaining=remaining,
        ),
    )
