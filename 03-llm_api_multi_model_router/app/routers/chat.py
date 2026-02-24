from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import router_service

router = APIRouter(prefix="/v1", tags=["chat"])


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    text: str
    provider: str
    model: str
    latency_ms: float
    fallback_used: bool


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        result = router_service(req.prompt)
        return ChatResponse(
            text=result.text,
            provider=result.provider,
            model=result.model,
            latency_ms=result.latency_ms,
            fallback_used=result.fallback_used,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(503, detail=str(e))
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
            raise HTTPException(503, detail="All providers rate limited or quota exceeded.")
        raise HTTPException(503, detail=str(e))
