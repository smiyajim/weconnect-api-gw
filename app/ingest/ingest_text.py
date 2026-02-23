# app/ingest/ingest_text.py

from app.ingest.chunker import chunk_text
from app.ingest.normalize import normalize_text
from app.embeddings import get_embedding_client
from app.ingest.repository import insert_documents_bulk
from app.ingest.text_normalizer import normalize_japanese_text
import logging

logger = logging.getLogger(__name__)

async def ingest_text(
    tenant_id: str,
    text: str,
    *,
    filename: str,
    page_no: int,
    source: str = "pdf",
):
    """
    Ingest pipeline

    - chunker は構造分割のみ
    - embedding 用テキスト生成は ingest 側
    - structure は meta に完全保持
    """

    # ------------------------------------------------------------------
    # ① 日本語PDF特有の正規化
    # ------------------------------------------------------------------
    text = normalize_japanese_text(text)

    # ------------------------------------------------------------------
    # ② 共通正規化
    # ------------------------------------------------------------------
    normalized_text = normalize_text(text)

    # ------------------------------------------------------------------
    # ③ chunking（唯一の正）
    # ------------------------------------------------------------------
    chunks = chunk_text(normalized_text)

    print("DEBUG chunk structures:")    # DEBUG
    for c in chunks[:5]:                # DEBUG
        print(c["structure"])           # DEBUG

    # ------------------------------------------------------------------
    # ④ embedding 用 contents / metas 作成
    # ------------------------------------------------------------------
    contents: list[str] = []
    metas: list[dict] = []

    for idx, chunk in enumerate(chunks):
        body = chunk.get("text")
        structure = chunk.get("structure", {})

        print("DEBUG meta.structure:", structure)   # DEBUG

        if not isinstance(body, str) or not body.strip():
            continue

        llm_parts: list[str] = []

        if structure.get("title"):
            llm_parts.append(f"【{structure['title']}】")

        if structure.get("section"):
            llm_parts.append(f"〔{structure['section']}〕")

        if structure.get("article"):
            llm_parts.append(structure["article"])

        llm_parts.append(body.strip())

        contents.append("\n".join(llm_parts))
        metas.append({
            "source": source,
            "filename": filename,
            "page": page_no,
            "chunk_index": idx,
            "structure": structure,
        })

    # ------------------------------------------------------------------
    # ⑤ safety（★今回の本題・最小）
    # ------------------------------------------------------------------
    if not contents:
        logger.warning("No valid contents for embedding, skip ingest")
        return

    # ------------------------------------------------------------------
    # ⑥ embedding
    # ------------------------------------------------------------------
    embedding_client = get_embedding_client()
    embeddings = await embedding_client.embed(contents)

    # ------------------------------------------------------------------
    # ⑦ DB insert
    # ------------------------------------------------------------------
    await insert_documents_bulk(
        customer_id=tenant_id,
        contents=contents,
        embeddings=embeddings,
        metas=metas,
    )