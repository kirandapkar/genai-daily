from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.rag_service import rag_ask, rag_ingest

router = APIRouter(prefix="/v1", tags=["rag"])


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    citations: list[str]


@router.post("/ingest")
def ingest(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, detail="Upload a PDF file.")
    try:
        pdf_bytes = file.file.read()
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    try:
        n = rag_ingest(pdf_bytes)
        return {"status": "ok", "chunks_ingested": n}
    except Exception as e:
        raise HTTPException(503, detail=str(e))


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        result = rag_ask(req.question)
        return AskResponse(answer=result.answer, citations=result.citations)
    except ValueError as e:
        raise HTTPException(503, detail=str(e))
    except Exception as e:
        raise HTTPException(503, detail=str(e))
