# app/embeddings/client.py

import os
from openai import AsyncOpenAI

EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small"  # 1536次元
)

class EmbeddingClient:
    def __init__(self):
        self.client = AsyncOpenAI()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        return [d.embedding for d in response.data]