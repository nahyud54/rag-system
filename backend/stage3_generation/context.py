"""Stage 3: Context preparation with U-shape reordering.

The 'Lost in the Middle' paper shows LLMs attend more to the beginning and end
of their context window. U-shape places highest-scoring docs at positions 0 and -1,
burying lower-scoring docs in the middle.
"""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class ContextPreparer:
    def reorder_u_shape(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(documents) <= 2:
            return documents
        left, right = [], []
        for i, doc in enumerate(documents):
            if i % 2 == 0:
                left.append(doc)
            else:
                right.append(doc)
        # left: 0, 2, 4 ...  right (reversed): ..., 5, 3, 1
        return left + right[::-1]

    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        parts = []
        for i, doc in enumerate(documents, 1):
            meta = doc.get("metadata", {})
            fname = meta.get("file_name", "Unknown")
            slide = meta.get("slide_number", "?")
            score = doc.get("rerank_score", doc.get("score", 0))
            parts.append(
                f"[Tài liệu {i} | {fname} | Slide {slide} | Score: {score:.3f}]\n{doc['text']}"
            )
        return "\n\n---\n\n".join(parts)

    def prepare(
        self, documents: List[Dict[str, Any]], strategy: str = "u_shape"
    ) -> Tuple[str, List[Dict[str, Any]]]:
        if strategy == "u_shape":
            ordered = self.reorder_u_shape(documents)
        else:
            ordered = list(documents)

        context = self.format_context(ordered)
        logger.info(f"Context prepared: {len(documents)} docs → {len(context)} chars")
        return context, ordered
