# app/ingest/pdf_loader.py

import re
from pypdf import PdfReader
from pathlib import Path
from io import BytesIO

def _cleanup_pdf_text(text: str) -> str:
    # 全角スペース含めて空白整理
    text = re.sub(r"[ \u3000]+", " ", text)

    # ヘッダ除去（会社名 + Confidential）
    text = re.sub(r"株 式 会 社 WeGrow.*?Confidential", "", text)

    return text.strip()

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
            # ★ノイズ除去
            text = _cleanup_pdf_text(text)

            print(
                f"DEBUG PDF page={i+1} len={len(text)} "
                f"head={text[:100].replace(chr(10),' ')}"
            )

            results.append((i + 1, text))

    return results