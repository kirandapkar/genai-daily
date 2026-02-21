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
    provider: str = "openrouter"  # openrouter | gemini
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
        settings.default_openrouter_model if req.provider == "openrouter" else settings.default_gemini_model
    )
    if req.provider == "openrouter":
        text = svc.complete_openrouter(req.prompt, model)
    elif req.provider == "gemini":
        text = svc.complete_gemini(req.prompt, model)
    else:
        raise HTTPException(422, detail="provider must be openrouter or gemini")
    return ChatResponse(text=text, provider=req.provider, model=model)
