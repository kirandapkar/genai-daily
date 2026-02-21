from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_settings
from app.services import LLMService

router = APIRouter(prefix="/v1", tags=["chat"])
_service: LLMService | None = None


def get_llm_service() -> LLMService:
    global _service
    if _service is None:
        _service = LLMService()
    return _service


class ChatRequest(BaseModel):
    prompt: str
    provider: str = "gemini"  # gemini | openrouter
    model: str | None = None


class ChatResponse(BaseModel):
    text: str
    provider: str
    model: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    settings = get_settings()
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
    except ValueError as e:
        raise HTTPException(503, detail=str(e))
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
            raise HTTPException(503, detail="Provider rate limit or quota exceeded. Try again later or use openrouter.")
        raise HTTPException(503, detail=str(e))
    return ChatResponse(text=text, provider=req.provider, model=model)
