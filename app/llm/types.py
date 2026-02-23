# app/llm/types.py

from typing import TypedDict, List, Any, Literal

class ToolCall(TypedDict):
    name: str
    arguments: dict

class LLMResponse(TypedDict, total=False):
    type: Literal["assistant", "tool_call"]
    content: str
    tool_calls: List[ToolCall]