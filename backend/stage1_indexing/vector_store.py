"""Stage 1: Vector Store - ChromaDB persistent storage"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """Persistent ChromaDB vector store."""

    def __init__(
        self,
        db_path: str = "./data/chroma_db",
        collection_name: str = "rag_documents",
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _init(self):
        if self._client is not None:
            return
        import chromadb
        os.makedirs(self.db_path, exist_ok=True)
        self._client = chromadb.PersistentClient(path=self.db_path)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB ready at {self.db_path} (docs={self._collection.count()})")

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> None:
        self._init()

        if ids is None:
            ids = []
            for i, m in enumerate(metadatas):
                fname = m.get("file_name", "doc")
                slide = m.get("slide_number", 0)
                chunk = m.get("chunk_index", 0)
                ids.append(f"{fname}_{slide}_{chunk}_{i}")

        # ChromaDB requires primitive metadata values
        clean_meta = []
        for m in metadatas:
            clean_meta.append(
                {k: v if isinstance(v, (str, int, float, bool)) else str(v) for k, v in m.items()}
            )

        batch = 500
        for i in range(0, len(texts), batch):
            self._collection.upsert(
                documents=texts[i : i + batch],
                embeddings=embeddings[i : i + batch],
                metadatas=clean_meta[i : i + batch],
                ids=ids[i : i + batch],
            )

        logger.info(f"Stored {len(texts)} vectors (total={self._collection.count()})")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        self._init()
        n = min(top_k, self.count())
        if n == 0:
            return []

        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        res = self._collection.query(**kwargs)
        results = []
        for i in range(len(res["documents"][0])):
            results.append({
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i],
                "score": float(1 - res["distances"][0][i]),
            })
        return results

    def count(self) -> int:
        self._init()
        return self._collection.count()

    def get_stats(self) -> Dict[str, Any]:
        self._init()
        return {
            "total_documents": self.count(),
            "collection_name": self.collection_name,
            "db_path": self.db_path,
        }

    def reset(self) -> None:
        self._init()
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Vector store reset")
