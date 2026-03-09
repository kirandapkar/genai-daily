from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.rag_service import rag_ask, rag_ingest

router = APIRouter(prefix="/v1", tags=["rag"])


class AskRequest(BaseModel):
    question: str
    metadata_filter: dict[str, str] | None = None


class AskResponse(BaseModel):
    answer: str
    citations: list[str]


@router.post("/ingest")
def ingest(
    file: UploadFile = File(...),
    source: str = "",
    filename: str = "",
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, detail="Upload a PDF file.")
    try:
        pdf_bytes = file.file.read()
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    fn = filename or (file.filename or "unknown")
    try:
        result = rag_ingest(pdf_bytes, source=source or fn, filename=fn)
        return {"status": "ok", "doc_id": result.doc_id, "chunks_ingested": result.chunks_ingested}
    except Exception as e:
        raise HTTPException(503, detail=str(e))


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        result = rag_ask(req.question, metadata_filter=req.metadata_filter)
        return AskResponse(answer=result.answer, citations=result.citations)
    except ValueError as e:
        raise HTTPException(503, detail=str(e))
    except Exception as e:
        raise HTTPException(503, detail=str(e))
