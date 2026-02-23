# app/rag_clients/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseRAG(ABC):
    @abstractmethod
    # def search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:

        """
        検索結果を返す
        """
        raise NotImplementedError