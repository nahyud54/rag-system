"""Stage 2: Base vector similarity retriever"""

import logging
from typing import Any, Dict, List

from stage1_indexing.embedding import EmbeddingModel
from stage1_indexing.vector_store import VectorStore

logger = logging.getLogger(__name__)


class VectorRetriever:
    def __init__(self, embedder: EmbeddingModel, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        query_emb = self.embedder.embed_query(query)
        results = self.vector_store.search(query_emb, top_k=top_k)

        if threshold > 0:
            results = [r for r in results if r["score"] >= threshold]

        logger.info(f"Retrieved {len(results)} docs for: {query[:60]}")
        return results
