# app/embeddings/client.py

import os
import asyncio
from typing import Literal

from openai import AsyncOpenAI

EmbeddingModelKey = Literal["openai", "para_multi", "all_mpnet", "sbert_ja"]

OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

ST_MODEL_ID_MAP: dict[EmbeddingModelKey, str] = {
    "para_multi": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    "all_mpnet": "sentence-transformers/all-mpnet-base-v2",
    "sbert_ja": "colorfulscoop/sbert-base-ja",
}


class EmbeddingClient:
    def __init__(self):
        self._openai = AsyncOpenAI()
        self._st_models: dict[str, object] = {}

    async def embed(self, texts: list[str], model_key: EmbeddingModelKey = "openai") -> list[list[float]]:
        if model_key == "openai":
            resp = await self._openai.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=texts,
            )
            return [d.embedding for d in resp.data]

        model_id = ST_MODEL_ID_MAP[model_key]
        model = self._get_or_load_st_model(model_id)

        embs = await asyncio.to_thread(
            model.encode,
            texts,
            normalize_embeddings=True,
        )
        return embs.tolist()

    def _get_or_load_st_model(self, model_id: str):
        m = self._st_models.get(model_id)
        if m is not None:
            return m

        from sentence_transformers import SentenceTransformer

        m = SentenceTransformer(model_id)
        self._st_models[model_id] = m
        return m
