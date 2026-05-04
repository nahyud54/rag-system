"""Stage 2: Multi-Query retrieval - generate query variations then deduplicate results"""

import logging
from typing import Any, Dict, List, Optional

from stage2_retrieval.retriever import VectorRetriever

logger = logging.getLogger(__name__)


class MultiQueryRetriever:
    def __init__(self, retriever: VectorRetriever, llm_client=None):
        self.retriever = retriever
        self.llm_client = llm_client

    def _generate_queries(self, query: str, num_queries: int = 3) -> List[str]:
        if self.llm_client and self.llm_client.is_available():
            prompt = (
                f"Tạo {num_queries} cách diễn đạt khác nhau cho câu hỏi sau để tìm kiếm tài liệu tốt hơn.\n"
                f"Chỉ xuất ra các câu hỏi, mỗi câu một dòng, không đánh số.\n\n"
                f"Câu hỏi gốc: {query}\n\nCác câu hỏi thay thế:"
            )
            try:
                response = self.llm_client.generate(prompt, temperature=0.7, max_tokens=200)
                lines = [l.strip() for l in response.strip().split("\n") if l.strip()]
                return [query] + lines[:num_queries]
            except Exception as e:
                logger.warning(f"LLM query generation failed, using fallback: {e}")

        # Heuristic fallback
        variations = [query]
        q_lower = query.lower()
        if q_lower.startswith("what "):
            variations.append("explain " + query[5:])
        elif q_lower.startswith("how "):
            variations.append("describe the process of " + query[4:])
        elif q_lower.startswith("why "):
            variations.append("the reason " + query[4:])
        return variations

    def retrieve(self, query: str, num_queries: int = 3, top_k: int = 5) -> List[Dict[str, Any]]:
        queries = self._generate_queries(query, num_queries)
        logger.info(f"Multi-query using {len(queries)} queries")

        seen: set = set()
        merged: List[Dict[str, Any]] = []

        for q in queries:
            for doc in self.retriever.retrieve(q, top_k=top_k):
                key = doc["text"][:100]
                if key not in seen:
                    seen.add(key)
                    merged.append(doc)

        merged.sort(key=lambda x: x["score"], reverse=True)
        return merged[: top_k * 2]
