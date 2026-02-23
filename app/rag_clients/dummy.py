# app/rag_clients/dummy.py

from app.rag_clients.base import BaseRAG

class DummyRAG(BaseRAG):
    def search(self, query: str, top_k: int):
        return [
            {
                "doc": "dummy result",
                "query": query
            }
        ]