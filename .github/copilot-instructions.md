# RAG System - AI Agent Instructions

## Project Overview

This is a **Retrieval-Augmented Generation (RAG) System** - a multi-stage pipeline for intelligent document processing and question-answering. The system has two main components:

- **Backend**: Python FastAPI server with 4-stage RAG pipeline
- **Frontend**: Next.js TypeScript UI for chat interface

## Architecture: 4-Stage Pipeline

Understanding the stage separation is critical:

```
Stage 1 (Indexing) → Stage 2 (Retrieval) → Stage 3 (Generation) → Stage 4 (Application)
```

### Stage 1: Indexing (`backend/stage1_indexing/`)
- **Purpose**: Transform raw documents into queryable embeddings
- **Flow**: Raw documents → Crawl → ETL (extract text) → Chunk → Embed → Store
- **Key Files**: `crawling.py`, `etl.py`, `chunking.py`, `embedding.py`
- **Router**: `indexing_router.py` at `/api/v1/indexing/*`
- **Outputs to**: Vector database (Chroma, Pinecone, or Weaviate)

### Stage 2: Retrieval (`backend/stage2_retrieval/`)
- **Purpose**: Find most relevant context for a query
- **Flow**: Query → Embed → Search → Multi-Query/HyDE → Re-rank → Return top-k
- **Key Files**: `retriever.py`, `multi_query.py`, `hyde.py`, `reranker.py`
- **Router**: `retrieval_router.py` at `/api/v1/retrieval/*`
- **Configuration**: `top_k_results`, `similarity_threshold`, `use_multi_query`, `use_hyde`, `use_reranking` in `config.py`

### Stage 3: Generation (`backend/stage3_generation/`)
- **Purpose**: Generate answers using LLM with retrieved context
- **Flow**: Context → Reorder (U-Shape) → LLM call → Parse output
- **Key Files**: `context.py`, `llm.py`, `parser.py`
- **Router**: `generation_router.py` at `/api/v1/generation/*`
- **LLM Support**: Qwen2.5, Llama (via Ollama at `http://localhost:11434`)

### Stage 4: Application (`backend/stage4_application/`)
- **Purpose**: Orchestrate complete pipeline for chat interface
- **Key File**: `rag_chain.py` - implements LangChain RAG chain
- **Router**: `chat_router.py` at `/api/v1/chat/message` - main user-facing endpoint

## Critical Development Patterns

### Configuration Management
- All settings in `backend/config.py` via Pydantic `BaseSettings`
- Environment variables override defaults (see `.env.example`)
- Access via `from config import settings` then `settings.setting_name`
- **Key settings for each stage**:
  - Indexing: `chunk_size`, `chunk_overlap`, `embedding_model`
  - Retrieval: `top_k_results`, `similarity_threshold`, retrieval flags
  - Generation: `llm_model`, `llm_temperature`, `llm_max_tokens`
  - Vector DB: `vector_db_type`, paths/keys for Chroma/Pinecone/Weaviate

### Router Pattern
All endpoints follow `/api/v1/{stage}/*` structure:
- Each stage has dedicated router in `routers/` directory
- Models defined in router file using Pydantic (`BaseModel`)
- HTTP method: POST for operations, GET for queries
- Always include `HTTPException` for error handling

**Example from `chat_router.py`**:
```python
@router.post("/message")
async def chat_message(request: ChatRequest) -> ChatResponse:
    # ChatRequest and ChatResponse are Pydantic models in same file
```

### Logging
- Uses `core/logger.py` with JSON formatting option (`log_format` setting)
- Access via `logger = setup_logging()` - already initialized in `main.py`
- Structured logging for production, text format for development

### Error Handling
- Use `HTTPException(status_code=..., detail="...")` for API errors
- Global exception handler in `main.py` catches unhandled exceptions
- Always log exceptions with `logger.error(..., exc_info=True)`

## Key Dependencies & Integrations

| Component | Library | Version | Notes |
|-----------|---------|---------|-------|
| API Framework | FastAPI | 0.104.1 | Automatic OpenAPI/Swagger docs at `/docs` |
| LLM Integration | LangChain | 0.1.5 | Abstracts LLM/embedding model calls |
| Vector Store | Chroma/Pinecone/Weaviate | Multiple | Configurable via `vector_db_type` |
| Embeddings | sentence-transformers | 2.2.2 | Default: `paraphrase-multilingual-MiniLM-L12-v2` |
| LLM Backend | Ollama | N/A | Default local: `http://localhost:11434` |
| Frontend | Next.js 14 | 14.0.0 | API client in `frontend/src/services/api.ts` |
| Document Processing | python-pptx, PyPDF2, python-docx | Various | ETL stage handles PPT/PDF/DOCX extraction |

## Development Workflows

### Starting Backend Development
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate, Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
# Configure .env with LLM_BASE_URL, embedding model, etc.
python main.py  # Starts on http://localhost:8000
```

### Testing Endpoints
- Swagger UI available at `http://localhost:8000/docs`
- Health checks: `/health`, `/health/ready`, `/health/live`
- Test stages independently: POST to `/api/v1/{stage}/*` endpoints

### Database & Persistence
- Vector data stored in `vector_db_path` (default: `./data/chroma_db`)
- Session data in-memory in `chat_router.py` (use DB in production)
- SQLAlchemy available for relational DB (see `database_url` in settings)

### Frontend Development
```bash
cd frontend
npm install
# Create .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev  # Starts on http://localhost:3000
```

## Common Customization Points

When extending the system, you'll frequently modify:

1. **Chunking strategy**: `stage1_indexing/chunking.py` - adjust `chunk_size`, `chunk_overlap`, splitting logic
2. **Retrieval ranking**: `stage2_retrieval/reranker.py` - tune `reranker_model`, `reranker_threshold`
3. **Context preparation**: `stage3_generation/context.py` - implement different U-Shape orderings or ranking
4. **LLM prompts**: `stage3_generation/llm.py` - system prompts, temperature, max_tokens
5. **Chat logic**: `stage4_application/rag_chain.py` - session management, memory, conversation history

## Docker Deployment

- `docker-compose.yml` orchestrates backend, frontend, and Ollama services
- Volumes mount code for development and persist data
- Backend communicates with Ollama at `http://ollama:11434`
- Frontend accesses backend at `http://localhost:8000` (from browser perspective)

## Testing & Quality

- `pytest` configured for unit tests
- Run: `pytest backend/` (assumes tests/ directory or test_*.py files)
- Code quality tools available: `black`, `flake8`, `isort`, `mypy`
- Type hints expected throughout codebase

## When Adding New Features

1. **New retrieval method?** Add to `stage2_retrieval/` and toggle via config flag
2. **New document type support?** Extend `stage1_indexing/etl.py`
3. **New LLM provider?** Implement in `stage3_generation/llm.py` using LangChain adapters
4. **New frontend component?** Add to `frontend/src/components/`, import in page
5. **New settings?** Add to `Settings` class in `config.py`, it auto-loads from `.env`

---

**Last Updated**: May 4, 2026  
**For detailed development setup**, see [DEVELOPMENT.md](../DEVELOPMENT.md)
