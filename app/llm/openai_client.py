# app/llm/openai_client.py

import json
import os
from openai import AsyncOpenAI
from typing import TypedDict, List, Dict, Any, Literal
from app.llm.types import LLMResponse

class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI()

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
    ) -> LLMResponse:

        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

        kwargs = {
            "model": model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self.client.chat.completions.create(**kwargs)

        msg = response.choices[0].message

        tool_calls = []
        if msg.tool_calls:
            tool_calls = [
                {
                    "id": call.id,  # ★ 重要
                    "name": call.function.name,
                    "arguments": json.loads(call.function.arguments),
                }
                for call in msg.tool_calls
            ]

        return {
            "type": "tool_call" if tool_calls else "assistant",
            "content": msg.content or "",
            "tool_calls": tool_calls,
        }