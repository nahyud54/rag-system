"""Stage 3: LLM client via Ollama (supports Qwen2.5, Llama 3.2, etc.)"""

import json
import logging
from typing import Iterator, Optional

import requests

logger = logging.getLogger(__name__)

RAG_PROMPT_TEMPLATE = """\
Bạn là trợ lý học tập AI chuyên về Deep Learning. Dựa vào các tài liệu được cung cấp bên dưới, \
hãy trả lời câu hỏi một cách chính xác, rõ ràng và súc tích bằng tiếng Việt.
Nếu tài liệu không đủ thông tin để trả lời, hãy nói rõ điều đó.

TÀI LIỆU THAM KHẢO:
{context}

CÂU HỎI: {query}

TRẢ LỜI:"""


class OllamaLLM:
    def __init__(
        self,
        model: str = "qwen2.5",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.temperature,
                "num_predict": max_tokens if max_tokens is not None else self.max_tokens,
            },
        }
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=180
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running."
            )
        except Exception as e:
            raise RuntimeError(f"LLM generation error: {e}")

    def stream(self, prompt: str, temperature: Optional[float] = None) -> Iterator[str]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else self.temperature,
                "num_predict": self.max_tokens,
            },
        }
        try:
            with requests.post(
                f"{self.base_url}/api/generate", json=payload, stream=True, timeout=180
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        data = json.loads(line)
                        if not data.get("done", False):
                            yield data.get("response", "")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running."
            )

    def build_rag_prompt(self, query: str, context: str) -> str:
        return RAG_PROMPT_TEMPLATE.format(context=context, query=query)

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []
