# app/llm/gemini_client.py

class GeminiClient:
    async def chat(self, prompt, tools):
        return {
            "type": "assistant",
            "content": "Gemini stub",
            "tool_calls": [],  # ← 必ず list を返す
        }