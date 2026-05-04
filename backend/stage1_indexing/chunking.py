"""Stage 1: Chunking - Split documents into overlapping text chunks"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def _split_text(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text] if len(text) >= self.min_chunk_size else []

        chunks: List[str] = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # Prefer splitting at sentence/paragraph boundary
            if end < len(text):
                for sep in [".\n", ". ", "\n\n", "\n"]:
                    boundary = text.rfind(sep, start + self.chunk_size // 2, end)
                    if boundary != -1:
                        end = boundary + len(sep)
                        break

            chunk = text[start:end].strip()
            if len(chunk) >= self.min_chunk_size:
                chunks.append(chunk)

            next_start = end - self.chunk_overlap
            if next_start <= start:
                next_start = start + 1
            start = next_start

        return chunks

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunked: List[Dict[str, Any]] = []

        for doc in documents:
            chunks = self._split_text(doc["text"])
            meta = doc.get("metadata", {})

            for idx, chunk in enumerate(chunks):
                chunked.append({
                    "text": chunk,
                    "metadata": {
                        **meta,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                    },
                })

        logger.info(f"Created {len(chunked)} chunks from {len(documents)} documents")
        return chunked
