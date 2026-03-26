# app/rag_clients/pgvector_rag.py

from typing import List, Dict, Any, Literal
import asyncio
import json

from sqlalchemy import text

from app.embeddings import get_embedding_client
from app.rag_clients.base import BaseRAG
from app.db.rag_async_session import rag_async_engine

# evaldb保存（evaldbを作っている前提）
#from app.evaldb.repository import insert_embedding_eval_run
from app.evaldb.repository import insert_embedding_eval_run_strict

EmbeddingModelKey = Literal["openai", "para_multi", "all_mpnet", "sbert_ja"]

EMBEDDING_COL_MAP: dict[EmbeddingModelKey, str] = {
    "openai": "embedding_openai",
    "para_multi": "embedding_para_multi",
    "all_mpnet": "embedding_all_mpnet",
    "sbert_ja": "embedding_sbert_ja",
}


class PgVectorRAG(BaseRAG):
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.embedding_client = get_embedding_client()

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] = None,  # フィルタ条件
        *,
        model_key: EmbeddingModelKey = "openai",
    ) -> List[Dict[str, Any]]:
        # ① query embedding（モデル切替）
        query_embedding = await self.embedding_client.embed([query], model_key=model_key)
        vector = query_embedding[0]
        vector_str = "[" + ",".join(f"{v:.6f}" for v in vector) + "]"

        # ② where clause
        where_clause = "WHERE customer_id = :customer_id"
        params = {
            "customer_id": self.tenant_id,
            "query_embedding": vector_str,
            "top_k": top_k,
        }

        if filter_metadata:
            where_clause += " AND meta @> CAST(:filter_meta AS jsonb)"
            params["filter_meta"] = json.dumps(filter_metadata)

        col = EMBEDDING_COL_MAP[model_key]

        # ③ vector search
        sql = text(f"""
            SELECT content, meta
            FROM documents
            {where_clause}
            ORDER BY {col} <-> CAST(:query_embedding AS vector)
            LIMIT :top_k
        """)

        async with rag_async_engine.connect() as conn:
            result = await conn.execute(sql, params)
            rows = result.all()

        return [{"doc": row[0], "meta": row[1]} for row in rows]

    async def search_eval_all_models(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] = None,
        *,
        persist_to_evaldb: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """同じ質問コンテキストで4モデルを自動で切り替えて検索し、結果を返す（任意でevaldbへ保存）。"""
        model_keys: list[EmbeddingModelKey] = ["openai", "para_multi", "all_mpnet", "sbert_ja"]

        tasks = [
            self.search(
                query=query,
                top_k=top_k,
                filter_metadata=filter_metadata,
                model_key=mk,
            )
            for mk in model_keys
        ]
        results_list = await asyncio.gather(*tasks)

        results_by_model: Dict[str, List[Dict[str, Any]]] = {
            mk: res for mk, res in zip(model_keys, results_list)
        }

        #if persist_to_evaldb:
        #    await insert_embedding_eval_run(
        #        customer_id=self.tenant_id,
        #        query=query,
        #        top_k=top_k,
        #        filter_metadata=filter_metadata,
        #        results_by_model=results_by_model,
        #    )
        if persist_to_evaldb:
            await insert_embedding_eval_run_strict(
                # customer_id=self.customer_id,
                customer_id=self.tenant_id,
                query=query,
                top_k=top_k,
                filter_meta=filter_metadata,
                results_by_model=results_by_model,
            )
        return results_by_model