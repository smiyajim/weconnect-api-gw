# app/agent/deps.py

from app.agent.simple_agent import SimpleAgent
from app.llm.base import get_llm_client
from app.mcp.client import MCPClient


def get_simple_agent():
    """
    FastAPI dependency.
    MCPClient is created lazily (runtime), not at import time.
    """
    llm = get_llm_client()
    mcp = MCPClient()   # ★ ここで初期化（安全）
    return SimpleAgent(llm=llm, mcp=mcp)