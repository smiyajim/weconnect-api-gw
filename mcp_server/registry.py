# mcp_server/registry.py

from mcp_server.schemas import rag_search_schema

def get_tool_definitions(tenant_id: str | None = None):
    """
    Return the list of tool definitions available for a tenant.
    Currently tenant_id is ignored (future-proofing)
    """
    # 今は tenant_id は使わない（将来用）
    return [
        {
            "type": "function",
            "function": rag_search_schema()
        }
    ]