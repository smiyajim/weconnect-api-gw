# app/ingest/repository.py

import uuid
from typing import List, Dict, Any
from sqlalchemy import text
from app.db.async_session import async_engine
import json

async def insert_documents_bulk(
    customer_id: str,
    contents: List[str],
    *,
    embeddings_openai: List[List[float]],
    embeddings_para_multi: List[List[float]],
    embeddings_all_mpnet: List[List[float]],
    embeddings_sbert_ja: List[List[float]],
    metas: List[Dict[str, Any]] = None,
):
    n = len(contents)
    assert n == len(embeddings_openai)
    assert n == len(embeddings_para_multi)
    assert n == len(embeddings_all_mpnet)
    assert n == len(embeddings_sbert_ja)
    if metas is None:
        metas = [None] * n

    def _vec_str(vec: List[float]) -> str:
        return "[" + ",".join(f"{v:.6f}" for v in vec) + "]"

    rows = [
        {
            "id": uuid.uuid4(),
            "customer_id": customer_id,
            "content": content,
            "embedding_openai": _vec_str(e_openai),
            "embedding_para_multi": _vec_str(e_para),
            "embedding_all_mpnet": _vec_str(e_all),
            "embedding_sbert_ja": _vec_str(e_ja),
            "meta": json.dumps(meta) if meta else None,
        }
        for content, e_openai, e_para, e_all, e_ja, meta in zip(
            contents,
            embeddings_openai,
            embeddings_para_multi,
            embeddings_all_mpnet,
            embeddings_sbert_ja,
            metas,
        )
    ]

    sql = text("""
        INSERT INTO documents (
            id,
            customer_id,
            content,
            embedding_openai,
            embedding_para_multi,
            embedding_all_mpnet,
            embedding_sbert_ja,
            meta
        )
        VALUES (
            :id,
            :customer_id,
            :content,
            CAST(:embedding_openai AS vector),
            CAST(:embedding_para_multi AS vector),
            CAST(:embedding_all_mpnet AS vector),
            CAST(:embedding_sbert_ja AS vector),
            CAST(:meta AS jsonb)
        )
    """)

    async with async_engine.begin() as conn:
        await conn.execute(sql, rows)