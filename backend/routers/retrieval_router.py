"""Stage 2: Retrieval endpoints"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from dependencies import get_embedder, get_vector_store
from stage2_retrieval.reranker import CrossEncoderReranker
from stage2_retrieval.retriever import VectorRetriever

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    threshold: Optional[float] = 0.0


class ReRankRequest(BaseModel):
    query: str
    documents: List[Dict[str, Any]]
    top_k: Optional[int] = 5


@router.post("/search")
async def vector_search(request: SearchRequest):
    """Vector similarity search."""
    retriever = VectorRetriever(get_embedder(), get_vector_store())
    results = retriever.retrieve(request.query, top_k=request.top_k, threshold=request.threshold)
    return {"query": request.query, "results": results, "count": len(results)}


@router.post("/rerank")
async def rerank_documents(request: ReRankRequest):
    """Re-rank documents using cross-encoder."""
    reranker = CrossEncoderReranker()
    results = reranker.rerank(request.query, request.documents, top_k=request.top_k)
    return {"query": request.query, "results": results, "count": len(results)}


@router.get("/stats")
async def retrieval_stats():
    """Vector store statistics."""
    vs = get_vector_store()
    return vs.get_stats()
