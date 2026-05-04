"""Singleton dependencies shared across all routers."""

import logging
from typing import Optional

from config import settings
from stage1_indexing.chunking import TextChunker
from stage1_indexing.embedding import EmbeddingModel
from stage1_indexing.etl import PPTXExtractor
from stage1_indexing.pipeline import IndexingPipeline
from stage1_indexing.vector_store import VectorStore
from stage3_generation.llm import OllamaLLM
from stage4_application.rag_chain import RAGChain

logger = logging.getLogger(__name__)

_embedder: Optional[EmbeddingModel] = None
_vector_store: Optional[VectorStore] = None
_llm: Optional[OllamaLLM] = None
_rag_chain: Optional[RAGChain] = None


def get_embedder() -> EmbeddingModel:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingModel(
            model_name=settings.embedding_model,
            device=settings.embedding_device,
        )
    return _embedder


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(db_path=settings.vector_db_path)
    return _vector_store


def get_llm() -> OllamaLLM:
    global _llm
    if _llm is None:
        _llm = OllamaLLM(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
    return _llm


def get_rag_chain() -> RAGChain:
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain(
            embedder=get_embedder(),
            vector_store=get_vector_store(),
            llm=get_llm(),
            use_multi_query=settings.use_multi_query,
            use_hyde=settings.use_hyde,
            use_reranking=settings.use_reranking,
            top_k=settings.top_k_results,
            similarity_threshold=settings.similarity_threshold,
        )
    return _rag_chain


def get_indexing_pipeline() -> IndexingPipeline:
    return IndexingPipeline(
        extractor=PPTXExtractor(),
        chunker=TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            min_chunk_size=settings.min_chunk_size,
        ),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )
