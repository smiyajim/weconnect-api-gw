# app/rag_clients/external_rag.py

class ExternalRAG:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    async def search(self, query: str, top_k: int = 5):
        # ダミーの結果を返すだけ
        return [{"doc": f"Dummy result for '{query}'"}]