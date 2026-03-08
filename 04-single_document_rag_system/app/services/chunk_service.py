from app.config import get_settings


def chunk_text(text: str) -> list[str]:
    settings = get_settings()
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    if not text or size <= 0:
        return [text] if text else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
        if start >= len(text):
            break
    return chunks if chunks else [text.strip()] if text.strip() else []
