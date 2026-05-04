"""Stage 4: RAG Chain - orchestrates all stages end-to-end"""

import logging
from typing import Any, Dict, Iterator, List, Optional

from stage1_indexing.embedding import EmbeddingModel
from stage1_indexing.vector_store import VectorStore
from stage2_retrieval.hyde import HyDERetriever
from stage2_retrieval.multi_query import MultiQueryRetriever
from stage2_retrieval.reranker import CrossEncoderReranker
from stage2_retrieval.retriever import VectorRetriever
from stage3_generation.context import ContextPreparer
from stage3_generation.llm import OllamaLLM
from stage3_generation.parser import StrOutputParser

logger = logging.getLogger(__name__)


class RAGChain:
    def __init__(
        self,
        embedder: EmbeddingModel,
        vector_store: VectorStore,
        llm: OllamaLLM,
        use_multi_query: bool = True,
        use_hyde: bool = False,
        use_reranking: bool = True,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
    ):
        self.llm = llm
        self.top_k = top_k

        base = VectorRetriever(embedder, vector_store)
        if use_hyde:
            self.retriever = HyDERetriever(base, llm)
        elif use_multi_query:
            self.retriever = MultiQueryRetriever(base, llm)
        else:
            self.retriever = base

        self.reranker = CrossEncoderReranker() if use_reranking else None
        self.context_preparer = ContextPreparer()
        self.parser = StrOutputParser()

    def _retrieve_and_rerank(self, query: str) -> List[Dict[str, Any]]:
        if isinstance(self.retriever, MultiQueryRetriever):
            docs = self.retriever.retrieve(query, top_k=self.top_k)
        elif isinstance(self.retriever, HyDERetriever):
            docs = self.retriever.retrieve(query, top_k=self.top_k)
        else:
            docs = self.retriever.retrieve(query, top_k=self.top_k)

        if self.reranker and docs:
            docs = self.reranker.rerank(query, docs, top_k=self.top_k)

        return docs

    def run(self, query: str) -> Dict[str, Any]:
        """Full RAG pipeline, returns complete response."""
        docs = self._retrieve_and_rerank(query)

        if not docs:
            return {
                "answer": "Không tìm thấy thông tin liên quan trong tài liệu.",
                "sources": [],
                "retrieved_count": 0,
            }

        context, ordered_docs = self.context_preparer.prepare(docs)
        prompt = self.llm.build_rag_prompt(query, context)
        raw = self.llm.generate(prompt)
        answer = self.parser.parse(raw)

        sources = [
            {
                "file": d.get("metadata", {}).get("file_name", "Unknown"),
                "course": d.get("metadata", {}).get("course_name", "Unknown"),
                "slide": d.get("metadata", {}).get("slide_number", "?"),
                "score": round(d.get("rerank_score", d.get("score", 0)), 3),
                "preview": d["text"][:200] + "..." if len(d["text"]) > 200 else d["text"],
            }
            for d in ordered_docs
        ]

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_count": len(docs),
        }

    def stream(self, query: str) -> Iterator[str]:
        """RAG pipeline with streaming LLM tokens."""
        docs = self._retrieve_and_rerank(query)

        if not docs:
            yield "Không tìm thấy thông tin liên quan trong tài liệu."
            return

        context, _ = self.context_preparer.prepare(docs)
        prompt = self.llm.build_rag_prompt(query, context)
        yield from self.llm.stream(prompt)
