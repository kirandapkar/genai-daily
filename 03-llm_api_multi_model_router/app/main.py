import logging

from fastapi import FastAPI

from app.routers import chat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
app = FastAPI(title="LLM API Multi-Model Router", version="0.1.0")
app.include_router(chat.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
