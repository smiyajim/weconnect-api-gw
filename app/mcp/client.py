# app/mcp/client.py

import httpx
import os
from typing import Dict, List, Any

class MCPClient:
    def __init__(self):
        self.url = os.getenv("MCP_SERVER_URL")
        if not self.url:
            raise RuntimeError("MCP_SERVER_URL is not set")

        self._tools_cache: Dict[str, List[Dict[str, Any]]] = {}

    async def initialize(self, tenant_id: str | None):
        """
        MCP handshake.
        - tools を取得
        - tenant ごとにキャッシュ
        """
        cache_key = tenant_id or "__default__"

        if cache_key in self._tools_cache:
            return  # すでに初期化済み

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.url}/initialize",
                json={"tenant_id": tenant_id},
                timeout=5.0,
            )
            r.raise_for_status()
            data = r.json()
            tools = data["tools"]
            if not isinstance(tools, list):
                raise RuntimeError("Invalid MCP initialize response: tools missing or not list")

            # ★ ここに来た場合のみキャッシュ
            self._tools_cache[cache_key] = tools

    async def get_tools(self, tenant_id: str | None = None):
        cache_key = tenant_id or "__default__"
        
        if cache_key not in self._tools_cache:
            await self.initialize(tenant_id)

        return self._tools_cache[cache_key]