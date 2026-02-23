# mcp_server/server.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
from mcp_server.registry import get_tool_definitions

class InitRequest(BaseModel):
    tenant_id: str | None = None

app = FastAPI(title="MCP Server")

@app.post("/initialize")
async def initialize(req: InitRequest):
    """
    MCP Handshake endpoint.
    """
    return {
        "protocol_version": "0.1",
        "capabilities": {
            "rag": True,
        },
        "tools": get_tool_definitions(tenant_id=req.tenant_id),
    }