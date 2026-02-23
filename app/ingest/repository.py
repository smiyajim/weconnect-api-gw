# app/ingest/repository.py

import uuid
from typing import List, Dict, Any
from sqlalchemy import text
from app.db.async_session import async_engine
import json

async def insert_documents_bulk(
    customer_id: str,
    contents: List[str],
    embeddings: List[List[float]],
    metas: List[Dict[str, Any]] = None, # [改修点] メタデータのリストを追加
):
    assert len(contents) == len(embeddings)
    if metas is None:
        metas = [None] * len(contents)
    
    rows = [
        {
            "id": uuid.uuid4(),
            "customer_id": customer_id,
            "content": content,
            "embedding": "[" + ",".join(f"{v:.6f}" for v in embedding) + "]",
            "meta": json.dumps(meta) if meta else None, # [改修点] JSON文字列として渡す
        }
        for content, embedding, meta in zip(contents, embeddings, metas)
    ]

    sql = text("""
        INSERT INTO documents (id, customer_id, content, embedding, meta)
        VALUES (:id, :customer_id, :content, CAST(:embedding AS vector), CAST(:meta AS jsonb))
    """)

    async with async_engine.begin() as conn:
        await conn.execute(sql, rows)