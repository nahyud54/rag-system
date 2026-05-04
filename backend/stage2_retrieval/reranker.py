"""Stage 2: Cross-encoder reranker"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Re-scores retrieved documents with a cross-encoder for better relevance ordering."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", threshold: float = 0.0):
        self.model_name = model_name
        self.threshold = threshold
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading cross-encoder: {self.model_name}")
            self._model = CrossEncoder(self.model_name)

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if not documents:
            return []

        self._load()
        pairs = [(query, doc["text"]) for doc in documents]
        scores = self._model.predict(pairs)

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        ranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)

        if self.threshold > 0:
            ranked = [d for d in ranked if d["rerank_score"] >= self.threshold]

        logger.info(f"Reranked {len(documents)} → {min(top_k, len(ranked))} docs")
        return ranked[:top_k]
