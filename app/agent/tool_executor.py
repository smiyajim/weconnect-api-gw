# app/agent/tool_executor.py

from app.tenant.resolver import resolve_rag_client
import asyncio
import logging

TOOL_TIMEOUT_SECONDS = 10  # ← 本番必須

async def execute_tool(tool_call: dict, tenant_id: str | None):
    try:
        return await asyncio.wait_for(
            _execute_tool_impl(tool_call, tenant_id),
            timeout=TOOL_TIMEOUT_SECONDS,
        )

    except asyncio.TimeoutError:
        logging.error(f"Tool timeout: {tool_call}")
        return {
            "tool_name": tool_call["name"],
            "error": "TOOL_TIMEOUT",
            "result": [],
        }

    except Exception as e:
        logging.exception("Tool execution error")
        return {
            "tool_name": tool_call["name"],
            "error": "TOOL_ERROR",
            "message": str(e),
            "result": [],
        }


async def _execute_tool_impl(tool_call: dict, tenant_id: str | None):
    name = tool_call["name"]
    args = tool_call["arguments"]
    
    if name == "rag_search":
        query = args["query"]
        top_k = args.get("top_k", 5)
        # [追加] メタデータ引数の取得
        filter_metadata = args.get("metadata")
        
        from app.tenant.resolver import resolve_rag_client
        rag = await resolve_rag_client(tenant_id)
        
        # 以前提示した PgVectorRAG.search(filter_metadata=...) を呼び出し
        result = await rag.search(query=query, top_k=top_k, filter_metadata=filter_metadata)
        
        return {
            "tool_name": name,
            "result": result,
        }
    raise ValueError(f"Unknown tool: {name}")