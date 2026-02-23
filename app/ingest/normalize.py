# app/ingest/normalize.py

import re

def normalize_text(text: str) -> str:
    text = text.replace("\u3000", " ")  # 全角スペース
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()