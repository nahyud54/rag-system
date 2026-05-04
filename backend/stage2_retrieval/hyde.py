"""Stage 2: HyDE - Hypothetical Document Embeddings retrieval"""

import logging
from typing import Any, Dict, List

from stage2_retrieval.retriever import VectorRetriever

logger = logging.getLogger(__name__)


class HyDERetriever:
    """Generate a hypothetical answer passage, embed it, then use it for retrieval.

    Addresses the query-document mismatch: queries are short while indexed chunks
    are longer passages — a hypothetical passage is a closer embedding match.
    """

    def __init__(self, retriever: VectorRetriever, llm_client=None):
        self.retriever = retriever
        self.llm_client = llm_client

    def _generate_hypothetical_doc(self, query: str) -> str:
        if self.llm_client and self.llm_client.is_available():
            prompt = (
                f"Viết một đoạn văn ngắn (2-3 câu) trả lời trực tiếp câu hỏi sau.\n"
                f"Chỉ viết đoạn văn trả lời, không thêm gì khác.\n\n"
                f"Câu hỏi: {query}\n\nĐoạn văn trả lời:"
            )
            try:
                return self.llm_client.generate(prompt, temperature=0.5, max_tokens=150)
            except Exception as e:
                logger.warning(f"HyDE generation failed, using query: {e}")
        return query

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        hyp_doc = self._generate_hypothetical_doc(query)
        logger.info(f"HyDE doc: {hyp_doc[:80]}...")
        return self.retriever.retrieve(hyp_doc, top_k=top_k)
