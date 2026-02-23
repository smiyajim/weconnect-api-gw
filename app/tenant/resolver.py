# app/tenant/resolver.py

from sqlalchemy import text
from fastapi import Header, HTTPException

from app.db.system_async_session import system_async_engine
from app.rag_clients.pgvector_rag import PgVectorRAG
from app.rag_clients.external_rag import ExternalRAG

async def resolve_tenant(
    tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
):
    return tenant_id or "default"

async def resolve_rag_client(
    tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
):
    if not tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")

    async with system_async_engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT
                    r.rag_type,
                    r.base_url,
                    r.api_key
                FROM customers c
                JOIN rag_endpoints r
                  ON c.id = r.customer_id
                WHERE c.id = :tenant_id
            """),
            {"tenant_id": tenant_id},
        )
        row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Tenant not found")

    rag_type, base_url, api_key = row

    # 🔽 RAG 実装の分岐（ここが唯一の分岐点）
    if rag_type == "pgvector":
        return PgVectorRAG(tenant_id=tenant_id)

    if rag_type == "external":
        return ExternalRAG(
            base_url=base_url,
            api_key=api_key,
        )

    raise HTTPException(
        status_code=500,
        detail=f"Unsupported rag_type: {rag_type}",
    )