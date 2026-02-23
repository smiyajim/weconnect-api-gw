# app/agent/simple_agent.py

from app.agent.tool_executor import execute_tool
import json


class SimpleAgent:
    """
    Responsibilities:
    - Fetch MCP tool definitions (per tenant)
    - Call LLM with prompt + tools
    - Return raw LLM result (no tool execution yet)
    """
    def __init__(self, llm, mcp):
        self.llm = llm
        self.mcp = mcp

    async def run(self, prompt: str, tenant_id: str | None):
        tools = await self.mcp.get_tools(tenant_id)

        # ① user message
        base_system_prompt = (
            "あなたは社内文書検索アシスタントです。\n\n"
            "- 社内規定・社内文書・就業規則・契約・規程・ルールに関する質問の場合は\n"
            "  必ず rag_search ツールを使用してください。\n"
            "- ツールを使わずに推測や一般知識で回答してはいけません。\n"
            "- 情報が見つからなかった場合は「見つかりませんでした」と答えてください。"
        )

        FORCE_TOOL_SYSTEM_PROMPT = (
            "あなたは社内文書検索アシスタントです。\n\n"
            "【重要】\n"
            "- この質問は必ず rag_search ツールを使用して回答してください\n"
            "- ツールを使わずに文章で回答してはいけません\n"
            "- 必ず rag_search を呼び出してください"
        )

        messages = [
            {"role": "system", "content": base_system_prompt},
            {"role": "user", "content": prompt}
        ]

        # ② first LLM call
        llm_result = await self.llm.chat(
            messages=messages,
            tools=tools,
        )

        # ③ tool_call が来た場合、通常フロー
        if llm_result["type"] == "tool_call":
            return await self._handle_tool_flow(llm_result, messages, tenant_id)

        # ④ tool を使わなかった場合、強制リトライ
        if llm_result["type"] == "assistant" and tools:
            # system prompt を強制版に差し替え
            messages[0] = {
                "role": "system",
                "content": FORCE_TOOL_SYSTEM_PROMPT,
            }

            retry_result = await self.llm.chat(messages=messages, tools=tools)

            if retry_result["type"] == "tool_call":
                return await self._handle_tool_flow(retry_result, messages, tenant_id)

            # 2回目も tool_call なし → 諦める
            return {
                "type": "assistant",
                "content": (
                    "社内文書検索が必要な質問でしたが、"
                    "検索ツールを実行できませんでした。"
                    "質問内容を見直してください。"
                ),
                "tenant_id": tenant_id,
            }

        # ⑤ tool 不要ケース（将来拡張用）
        return {
            "type": "assistant",
            "content": llm_result["content"],
            "tenant_id": tenant_id,
        }

    async def _handle_tool_flow(self, llm_result, messages, tenant_id):
        assistant_message = {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": call["id"],
                    "type": "function",
                    "function": {
                        "name": call["name"],
                        "arguments": json.dumps(call["arguments"]),
                    },
                }
                for call in llm_result["tool_calls"]
            ],
        }
        messages.append(assistant_message)

        tool_results = []

        for call in llm_result["tool_calls"]:
            tool_result = await execute_tool(call, tenant_id)
            tool_results.append(tool_result)

            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(tool_result),
            })

        final = await self.llm.chat(messages=messages, tools=None)

        return {
            "type": "assistant",
            "content": final["content"],
            "tenant_id": tenant_id,
            "tool_results": tool_results,
        }