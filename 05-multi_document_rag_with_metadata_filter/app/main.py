import logging

from fastapi import FastAPI

from app.routers import rag

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
app = FastAPI(title="Multi-Document RAG with Metadata Filter", version="0.1.0")
app.include_router(rag.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
