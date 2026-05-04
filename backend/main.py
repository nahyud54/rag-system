#!/usr/bin/env python3
"""
RAG System - FastAPI Main Entry Point

Multi-stage Retrieval-Augmented Generation system:
- Stage 1: Indexing (crawling, ETL, chunking, embedding)
- Stage 2: Retrieval (search, multi-query, HyDE, reranking)
- Stage 3: Generation (context, LLM, parsing)
- Stage 4: Application (RAG chain, chat interface)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging

from config import settings
from core.logger import setup_logging
from routers import (
    health_router,
    indexing_router,
    retrieval_router,
    generation_router,
    chat_router,
)

# Setup logging
logger = setup_logging()

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 RAG System starting up...")
    logger.info(f"Environment: {settings.debug and 'DEBUG' or 'PRODUCTION'}")
    logger.info(f"LLM Model: {settings.llm_model}")
    logger.info(f"Embedding Model: {settings.embedding_model}")
    logger.info(f"Vector DB: {settings.vector_db_type}")
    yield
    # Shutdown
    logger.info("🛑 RAG System shutting down...")

# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="""
    Retrieval-Augmented Generation (RAG) System API
    
    ## Features:
    - **Stage 1: Indexing** - Crawl, ETL, chunk, embed documents
    - **Stage 2: Retrieval** - Vector search, multi-query, HyDE, reranking
    - **Stage 3: Generation** - Context preparation, LLM integration
    - **Stage 4: Application** - Complete RAG pipeline with chat
    
    ## Quick Start:
    1. Use POST /api/v1/indexing/* endpoints to index documents
    2. Use POST /api/v1/retrieval/* endpoints to search
    3. Use POST /api/v1/generation/* endpoints to generate answers
    4. Use POST /api/v1/chat/message for complete pipeline
    """,
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred",
        },
    )

# Include routers
app.include_router(health_router.router, tags=["Health"])
app.include_router(
    indexing_router.router,
    prefix="/api/v1",
    tags=["Stage 1: Indexing"],
)
app.include_router(
    retrieval_router.router,
    prefix="/api/v1",
    tags=["Stage 2: Retrieval"],
)
app.include_router(
    generation_router.router,
    prefix="/api/v1",
    tags=["Stage 3: Generation"],
)
app.include_router(
    chat_router.router,
    prefix="/api/v1",
    tags=["Stage 4: Application"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "RAG System API",
        "version": "1.0.0",
        "description": "Retrieval-Augmented Generation System",
        "documentation": "http://localhost:8000/docs",
        "endpoints": {
            "health": "/health",
            "indexing": "/api/v1/indexing/*",
            "retrieval": "/api/v1/retrieval/*",
            "generation": "/api/v1/generation/*",
            "chat": "/api/v1/chat/*",
        },
        "status": "running",
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.fast_api_host,
        port=settings.fast_api_port,
        reload=settings.debug,
    )
