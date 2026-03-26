# app/evaldb/repository.py

import uuid
import json
from typing import Any, Dict
from sqlalchemy import text
from datetime import datetime

from app.db.eval_async_session import eval_async_engine

async def insert_embedding_eval_run_strict(
    *,
    customer_id: str,
    query: str,
    top_k: int,
    filter_meta: dict | None,
    results_by_model: dict,
) -> uuid.UUID:

    run_id = uuid.uuid4()

    sql_run = text("""
    INSERT INTO embedding_eval_runs (id, customer_id, query, top_k, filter_meta, created_at)
    VALUES (:id, :customer_id, :query, :top_k, CAST(:filter_meta AS jsonb), :created_at)
    """)

    sql_result = text("""
    INSERT INTO embedding_eval_results (id, run_id, model_key, results, created_at)
    VALUES (:id, :run_id, :model_key, CAST(:results AS jsonb), :created_at)
    """)

    now = datetime.utcnow()

    run_row = {
        "id": str(run_id),
        "customer_id": customer_id,
        "query": query,
        "top_k": int(top_k),
        "filter_meta": json.dumps(filter_meta or {}, ensure_ascii=False),
        "created_at": now,
    }

    result_rows = []
    for model_key, hits in results_by_model.items():
        result_rows.append({
            "id": str(uuid.uuid4()),
            "run_id": str(run_id),
            "model_key": model_key,
            "results": json.dumps(hits, ensure_ascii=False),
            "created_at": now,
        })

    async with eval_async_engine.begin() as conn:
        await conn.execute(sql_run, run_row)
        await conn.execute(sql_result, result_rows)

    return run_id

async def insert_embedding_eval_run(
    *,
    customer_id: str,
    query: str,
    top_k: int,
    filter_metadata: Dict[str, Any] | None,
    results_by_model: Dict[str, Any],
) -> uuid.UUID:
    run_id = uuid.uuid4()
    run_row = {
        "id": run_id,
        "customer_id": customer_id,
        "query": query,
        "top_k": top_k,
        "filter_meta": json.dumps(filter_metadata) if filter_metadata else None,
    }
    result_rows = [
        {
            "id": uuid.uuid4(),
            "run_id": run_id,
            "model_key": model_key,
            "results": json.dumps(model_results),
        }
        for model_key, model_results in results_by_model.items()
    ]

    sql_run = text("""
        INSERT INTO embedding_eval_runs (id, customer_id, query, top_k, filter_meta)
        VALUES (:id, :customer_id, :query, :top_k, CAST(:filter_meta AS jsonb))
    """)

    sql_result = text("""
        INSERT INTO embedding_eval_results (id, run_id, model_key, results)
        VALUES (:id, :run_id, :model_key, CAST(:results AS jsonb))
    """)

    async with eval_async_engine.begin() as conn:
        await conn.execute(sql_run, run_row)
        await conn.execute(sql_result, result_rows)

    return run_id