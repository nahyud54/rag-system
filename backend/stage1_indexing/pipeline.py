"""Stage 1: Indexing Pipeline - orchestrates ETL → chunk → embed → store"""

import logging
from typing import Any, Dict

from stage1_indexing.chunking import TextChunker
from stage1_indexing.embedding import EmbeddingModel
from stage1_indexing.etl import PPTXExtractor
from stage1_indexing.vector_store import VectorStore

logger = logging.getLogger(__name__)


class IndexingPipeline:
    def __init__(
        self,
        extractor: PPTXExtractor,
        chunker: TextChunker,
        embedder: EmbeddingModel,
        vector_store: VectorStore,
    ):
        self.extractor = extractor
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    def index_directory(self, directory: str) -> Dict[str, Any]:
        logger.info(f"Indexing directory: {directory}")

        docs = self.extractor.extract_from_directory(directory)
        if not docs:
            return {"error": "No documents found", "files_processed": 0}

        chunks = self.chunker.chunk_documents(docs)

        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        logger.info(f"Embedding {len(texts)} chunks...")
        embeddings = self.embedder.embed(texts)

        self.vector_store.add_documents(texts, embeddings, metadatas)

        files = {d["metadata"]["file_name"] for d in docs}
        return {
            "files_processed": len(files),
            "slides_extracted": len(docs),
            "chunks_created": len(chunks),
            "vectors_stored": self.vector_store.count(),
        }

    def index_file(self, file_path: str) -> Dict[str, Any]:
        docs = self.extractor.extract_from_file(file_path)
        chunks = self.chunker.chunk_documents(docs)

        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        embeddings = self.embedder.embed(texts)

        self.vector_store.add_documents(texts, embeddings, metadatas)

        return {
            "slides_extracted": len(docs),
            "chunks_created": len(chunks),
            "vectors_stored": self.vector_store.count(),
        }
