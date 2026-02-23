# app/rag_clients/pgvector_rag.py

from typing import List, Dict, Any
from sqlalchemy import text
from app.embeddings import get_embedding_client
from app.rag_clients.base import BaseRAG
from app.db.rag_async_session import rag_async_engine
import json

class PgVectorRAG(BaseRAG):
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.embedding_client = get_embedding_client()

    async def search(
        self, 
        query: str, 
        top_k: int = 5, 
        filter_metadata: Dict[str, Any] = None # [改修点] フィルタ条件を追加
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.embedding_client.embed([query])
        vector = query_embedding[0]
        vector_str = "[" + ",".join(f"{v:.6f}" for v in vector) + "]"

        # [改修点] 動的SQLの構築
        where_clause = "WHERE customer_id = :customer_id"
        params = {
            "customer_id": self.tenant_id,
            "query_embedding": vector_str,
            "top_k": top_k,
        }

        if filter_metadata:
            where_clause += " AND meta @> :filter_meta"
            params["filter_meta"] = json.dumps(filter_metadata)

        sql = text(f"""
            SELECT content, meta
            FROM documents
            {where_clause}
            ORDER BY embedding <-> CAST(:query_embedding AS vector)
            LIMIT :top_k
        """)

        async with rag_async_engine.connect() as conn:
            result = await conn.execute(sql, params)
            rows = result.all()
        
        return [{"doc": row[0], "meta": row[1]} for row in rows]