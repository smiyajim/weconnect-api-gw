# app/scripts/backfill_embeddings_768.py
#
# One-shot backfill script:
# - Fill documents.embedding_para_multi / embedding_all_mpnet / embedding_sbert_ja
# - Keep embedding_openai (1536) untouched
#
# Usage examples:
#   python -m app.scripts.backfill_embeddings_768 --batch-size 128
#   python -m app.scripts.backfill_embeddings_768 --customer-id <TENANT_ID> --batch-size 64
#   python -m app.scripts.backfill_embeddings_768 --dry-run
#
# Required env:
#   RAG_DATABASE_URL (already used by rag_async_engine)
#
import argparse
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text

from app.db.rag_async_session import rag_async_engine
from app.embeddings import get_embedding_client

logger = logging.getLogger("backfill_embeddings_768")


MODEL_KEYS = ["para_multi", "all_mpnet", "sbert_ja"]

COL_BY_MODEL = {
    "para_multi": "embedding_para_multi",
    "all_mpnet": "embedding_all_mpnet",
    "sbert_ja": "embedding_sbert_ja",
}


def _vec_str(vec: List[float]) -> str:
    # pgvector text input format: [0.1,0.2,...]
    return "[" + ",".join(f"{v:.6f}" for v in vec) + "]"


def _build_select_sql(customer_id: Optional[str], after_id: Optional[str]) -> Tuple[str, Dict[str, Any]]:
    where = """
      (embedding_para_multi IS NULL
       OR embedding_all_mpnet IS NULL
       OR embedding_sbert_ja IS NULL)
    """
    params: Dict[str, Any] = {}

    if customer_id:
        where += " AND customer_id = :customer_id"
        params["customer_id"] = customer_id

    if after_id is not None:
        where += " AND id > :after_id"
        params["after_id"] = after_id

    sql = f"""
      SELECT id, content,
             embedding_para_multi IS NULL AS need_para,
             embedding_all_mpnet IS NULL AS need_all,
             embedding_sbert_ja IS NULL AS need_ja
      FROM documents
      WHERE {where}
      ORDER BY id
      LIMIT :limit
    """
    return sql, params

def _build_update_sql() -> str:
    # Update only columns provided (can be NULL-safe)
    # We always pass values for needed cols, else pass None and keep existing via COALESCE
    return """
      UPDATE documents
      SET
        embedding_para_multi = COALESCE(CAST(:embedding_para_multi AS vector), embedding_para_multi),
        embedding_all_mpnet  = COALESCE(CAST(:embedding_all_mpnet  AS vector), embedding_all_mpnet),
        embedding_sbert_ja   = COALESCE(CAST(:embedding_sbert_ja   AS vector), embedding_sbert_ja)
      WHERE id = :id
    """


async def _fetch_batch(
    customer_id: Optional[str],
    after_id: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    #select_sql, params = _build_select_sql(customer_id)
    #params = dict(params)
    #params["after_id"] = after_id
    #params["limit"] = limit
    select_sql, params = _build_select_sql(customer_id, after_id)
    params["limit"] = limit

    async with rag_async_engine.connect() as conn:
        result = await conn.execute(text(select_sql), params)
        rows = result.mappings().all()
        return [dict(r) for r in rows]


async def _update_batch(rows: List[Dict[str, Any]], dry_run: bool) -> int:
    if dry_run:
        return len(rows)

    update_sql = _build_update_sql()
    async with rag_async_engine.begin() as conn:
        await conn.execute(text(update_sql), rows)
    return len(rows)


async def main():
    parser = argparse.ArgumentParser(description="Backfill 768-dim embedding columns for documents.")
    parser.add_argument("--customer-id", default=None, help="Optional tenant/customer_id to restrict.")
    parser.add_argument("--batch-size", type=int, default=128, help="Batch size (default: 128).")
    parser.add_argument("--max-batches", type=int, default=0, help="Stop after N batches (0 = no limit).")
    parser.add_argument("--dry-run", action="store_true", help="Compute counts only (no DB updates).")
    parser.add_argument("--log-level", default="INFO", help="Logging level (default: INFO).")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    embedding_client = get_embedding_client()

    after_id: Optional[str] = None
    batch_no = 0
    total_updated = 0

    t0 = time.time()
    logger.info("Starting backfill. customer_id=%s batch_size=%d dry_run=%s",
                args.customer_id, args.batch_size, args.dry_run)

    while True:
        if args.max_batches and batch_no >= args.max_batches:
            logger.info("Reached max_batches=%d. Stopping.", args.max_batches)
            break

        batch = await _fetch_batch(args.customer_id, after_id, args.batch_size)
        if not batch:
            break

        batch_no += 1
        after_id = str(batch[-1]["id"])

        # Only embed texts for columns actually missing in this batch.
        # But easiest (and still OK) is to embed all texts per model then apply only to needed rows.
        contents = [r["content"] for r in batch]

        # Compute 3 models in parallel
        emb_para_task = embedding_client.embed(contents, model_key="para_multi")
        emb_all_task = embedding_client.embed(contents, model_key="all_mpnet")
        emb_ja_task = embedding_client.embed(contents, model_key="sbert_ja")

        emb_para, emb_all, emb_ja = await asyncio.gather(emb_para_task, emb_all_task, emb_ja_task)

        # Build update rows (use None for columns that aren't needed so COALESCE keeps old value)
        update_rows: List[Dict[str, Any]] = []
        for i, row in enumerate(batch):
            update_rows.append({
                "id": row["id"],
                "embedding_para_multi": _vec_str(emb_para[i]) if row["need_para"] else None,
                "embedding_all_mpnet": _vec_str(emb_all[i]) if row["need_all"] else None,
                "embedding_sbert_ja": _vec_str(emb_ja[i]) if row["need_ja"] else None,
            })

        updated = await _update_batch(update_rows, args.dry_run)
        total_updated += updated

        elapsed = time.time() - t0
        logger.info("Batch %d: rows=%d total=%d elapsed=%.1fs after_id=%s",
                    batch_no, updated, total_updated, elapsed, after_id)

    elapsed = time.time() - t0
    logger.info("Done. batches=%d total_rows=%d elapsed=%.1fs dry_run=%s",
                batch_no, total_updated, elapsed, args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
