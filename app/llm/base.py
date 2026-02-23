# app/llm/base.py

import os
from app.llm.openai_client import OpenAIClient
from app.llm.gemini_client import GeminiClient
from typing import Protocol, Any, List, Dict
from app.llm.types import LLMResponse

class LLMClient(Protocol):
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
    ) -> LLMResponse:
        ...

def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "openai")
    if provider == "gemini":
        return GeminiClient()
    return OpenAIClient()