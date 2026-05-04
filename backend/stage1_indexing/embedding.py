"""Stage 1: Embedding - Sentence-transformer embeddings"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wraps sentence-transformers for text embedding."""

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu",
    ):
        self.model_name = model_name
        self.device = device
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Embedding model loaded (dim={self.dimension})")

    def embed(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        self._load()
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 50,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        self._load()
        embedding = self._model.encode(
            [text], normalize_embeddings=True, convert_to_numpy=True
        )
        return embedding[0].tolist()

    @property
    def dimension(self) -> int:
        self._load()
        return self._model.get_sentence_embedding_dimension()
