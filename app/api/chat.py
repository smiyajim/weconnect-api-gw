# app/api/chat.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.agent.simple_agent import SimpleAgent
from app.agent.deps import get_simple_agent
from app.tenant.resolver import resolve_tenant
from app.api.dependencies import require_internal_auth
from sqlalchemy import text
from app.db.rag_async_session import rag_async_engine
from app.logging.access_log import log_access

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

# ----------------------------------------
# Temporary minimal implementation
# ----------------------------------------
async def check_db() -> bool:
    try:
        async with rag_async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print("DB CHECK ERROR:", repr(e))
        return False
# ----------------------------------------

@router.post("/chat")
async def chat(
    req: ChatRequest,
    auth=Depends(require_internal_auth),
    tenant_id: str = Depends(resolve_tenant),  
    agent: SimpleAgent = Depends(get_simple_agent),
):
    # ★ AccessLog（最小）
    await log_access(
        tenant_id=tenant_id,
        endpoint="/chat",
        action="chat",
        meta={
            "prompt_len": len(req.prompt),
        }
    )

    return await agent.run(req.prompt, tenant_id)

@router.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

@router.get("/health/ready", tags=["health"])
async def readiness_check():
    db_ok = False
    try:
        print(db_ok)
        db_ok = await check_db()
        print(db_ok)
    except Exception:
        pass

    return {
        "status": "ok",
        "db": "ok" if db_ok else "degraded"
    }