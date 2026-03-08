from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.services.pdf_service import extract_text_from_pdf


def test_extract_text_from_pdf_empty() -> None:
    # Minimal PDF with no text
    w = PdfWriter()
    w.add_blank_page(width=72, height=72)
    buf = BytesIO()
    w.write(buf)
    text = extract_text_from_pdf(buf.getvalue())
    assert isinstance(text, str)


def test_extract_text_from_pdf_with_text() -> None:
    w = PdfWriter()
    w.add_blank_page(width=72, height=72)
    buf = BytesIO()
    w.write(buf)
    text = extract_text_from_pdf(buf.getvalue())
    assert isinstance(text, str)
