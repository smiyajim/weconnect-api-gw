# app/ingest/pdf_loader.py

from pypdf import PdfReader
from pathlib import Path
from io import BytesIO


def load_pdf_text(path: str | Path) -> str:
    reader = PdfReader(str(path))

    texts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)

    return "\n".join(texts)

# ★ 追加：APIアップロード用
def load_pdf_pages(raw: bytes) -> list[tuple[int, str]]:
    reader = PdfReader(BytesIO(raw))

    results: list[tuple[int, str]] = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            results.append((i + 1, text))

    return results