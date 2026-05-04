"""Stage 3: Output parsing - clean and structure LLM responses"""

import re
from typing import Any, Dict, List


class StrOutputParser:
    """Cleans raw LLM text output."""

    def parse(self, text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        # Collapse runs of 3+ newlines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove leading/trailing blank lines
        text = text.strip("\n")
        return text

    def parse_with_sources(
        self, text: str, sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        return {
            "answer": self.parse(text),
            "sources": sources,
        }
