# app/ingest/chunker.py

import re
from typing import List, Dict, Any

# =========================
# Public API
# =========================
def chunk_text(text: str, max_chars: int = 800) -> List[Dict[str, Any]]:
    """
    文書タイプを自動判別して最適な chunker を選択する
    """
    text = text.strip()

    print("LOOKS_LIKE_REGULATION:", _looks_like_regulation(text))   # DEBUG

    if _looks_like_regulation(text):
        chunks = _chunk_by_article(text)
    elif _looks_like_structured_doc(text):
        chunks = _chunk_by_heading(text)
    else:
        chunks = _chunk_by_paragraph(text)
    # セーフティ：巨大 chunk を分割
    final_chunks: List[Dict[str, Any]] = []

    for chunk in chunks:
        body = chunk["body"]
        parts = _split_large_chunk(body, max_chars)

        for part in parts:
            final_chunks.append({
                "text": part,
                "structure": chunk["structure"],
            })

    final_chunks = [c for c in final_chunks if len(c["text"]) >= 30]

    if not final_chunks:
        # 正常系：今回は ingest する chunk がなかっただけ
        return []

    return final_chunks

# =========================
# Heuristics
# =========================
def _looks_like_regulation(text: str) -> bool:
    """
    条項型文書（就業規則・契約書）っぽいか
    """
    # 改行・空白・全角空白を除去
    normalized = re.sub(r"[\s\u3000]+", "", text)

    # 第◯条 が1つでもあれば条文型
    return bool(re.search(
        r"第[0-9０-９一二三四五六七八九十]+条",
        normalized
    ))

def _looks_like_structured_doc(text: str) -> bool:
    """
    見出し構造のある文書か（技術仕様書など）
    """
    return bool(re.search(r"^\s*(\d+\.|\d+\)|#+\s)", text, re.MULTILINE))

# =========================
# Chunk strategies
# =========================
def _chunk_by_article(text: str) -> List[Dict[str, Any]]:
    """
    第◯条 単位で分割（次の第◯条までを本文とする）
    """
    pattern = re.compile(
        r"(第\s*[0-9０-９一二三四五六七八九十]+\s*条)"
    )

    matches = list(pattern.finditer(text))
    chunks = []

    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        title = m.group(1).strip()
        body = text[start:end].strip()

        if body:
            chunks.append(_build_chunk(
                title=title,
                body=body,
                structure_type="article",
                index=title,
            ))
    return chunks

def _chunk_by_heading(text: str) -> List[Dict[str, Any]]:
    """
    見出し単位（1. / 1) / ##）で分割
    """
    pattern = re.compile(
        r"(^\s*(?:\d+\.|\d+\)|#+\s).*)",
        re.MULTILINE,
    )
    parts = pattern.split(text)

    chunks = []
    title = "本文"

    for part in parts:
        if pattern.match(part):
            title = part.strip()
        elif part.strip():
            chunks.append(_build_chunk(
                title=title,
                body=part,
                structure_type="heading",
                index=None,
            ))

    return chunks

def _chunk_by_paragraph(text: str) -> List[Dict[str, Any]]:
    """
    空行ベースの段落分割
    """
    parts = re.split(r"\n\s*\n", text)
    return [
        _build_chunk(
            title="本文",
            body=p,
            structure_type="paragraph",
            index=None,
        )
        for p in parts if p.strip()
    ]

# =========================
# Safety
# =========================
def _build_chunk(*, title: str, body: str, structure_type: str, index: Any):
    return {
        "body": body.strip(),
        "structure": {
            "type": structure_type,
            "title": title,
            "index": index,
        },
    }

def _split_large_chunk(text: str, max_chars: int) -> List[str]:
    """
    embedding 上限対策：大きすぎる chunk を分割
    """
    if len(text) <= max_chars:
        return [text]

    return [
        text[i : i + max_chars]
        for i in range(0, len(text), max_chars)
    ]