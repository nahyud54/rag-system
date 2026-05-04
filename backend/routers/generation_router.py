"""Stage 3: Generation endpoints"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from dependencies import get_llm
from stage3_generation.context import ContextPreparer
from stage3_generation.parser import StrOutputParser

router = APIRouter(prefix="/generation", tags=["Generation"])

_context_preparer = ContextPreparer()
_parser = StrOutputParser()


class ContextRequest(BaseModel):
    documents: List[dict]
    query: str
    reorder_strategy: Optional[str] = "u_shape"


class GenerateRequest(BaseModel):
    context: str
    query: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ParseRequest(BaseModel):
    text: str


@router.post("/context")
async def prepare_context(request: ContextRequest):
    """Prepare and U-shape reorder context from retrieved documents."""
    context, ordered = _context_preparer.prepare(request.documents, request.reorder_strategy)
    return {
        "context": context,
        "ordered_documents": ordered,
        "document_count": len(ordered),
        "context_length": len(context),
    }


@router.post("/generate")
async def generate_answer(request: GenerateRequest):
    """Generate answer using the configured LLM via Ollama."""
    llm = get_llm()
    if not llm.is_available():
        raise HTTPException(status_code=503, detail="Ollama is not available")

    prompt = llm.build_rag_prompt(request.query, request.context)
    raw = llm.generate(prompt, temperature=request.temperature, max_tokens=request.max_tokens)
    answer = _parser.parse(raw)
    return {"query": request.query, "answer": answer}


@router.post("/parse")
async def parse_output(request: ParseRequest):
    """Clean and format raw LLM output."""
    return {"parsed": _parser.parse(request.text)}


@router.get("/llm-status")
async def llm_status():
    """Check if Ollama is running and list available models."""
    llm = get_llm()
    available = llm.is_available()
    return {
        "available": available,
        "base_url": llm.base_url,
        "current_model": llm.model,
        "models": llm.list_models() if available else [],
    }
