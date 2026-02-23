# app/embeddings/__init__.py

from .client import EmbeddingClient

_embedding_client: EmbeddingClient | None = None

def get_embedding_client() -> EmbeddingClient:
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = EmbeddingClient()
    return _embedding_client