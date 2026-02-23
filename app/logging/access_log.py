# app/logging/access_log.py

from uuid import uuid4
from app.systemdb.session import SessionLocal
from app.systemdb.models import AccessLog

def save_access_log(
    *,
    tenant_id: str,
    prompt: str,
    tool_used: str | None = None,
    tool_result: dict | None = None,
    llm_response: str | None = None,
):
    db = SessionLocal()
    try:
        log = AccessLog(
            id=str(uuid4()),
            tenant_id=tenant_id,
            prompt=prompt,
            tool_used=tool_used,
            tool_result=tool_result,
            llm_response=llm_response,
        )
        db.add(log)
        db.commit()
    finally:
        db.close()

async def log_access(
    tenant_id: str,
    endpoint: str,
    action: str,
    meta: dict | None = None,
):
    print({
        "tenant": tenant_id,
        "endpoint": endpoint,
        "action": action,
        "meta": meta,
    })