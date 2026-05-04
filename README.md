# 🤖 RAG System - Retrieval-Augmented Generation

A comprehensive Retrieval-Augmented Generation (RAG) system with multi-stage pipeline for knowledge extraction, embedding, retrieval, and generation. Built with FastAPI, LangChain, and Next.js.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  STAGE 1: INDEXING          STAGE 2: RETRIEVAL                │
│  ├─ Crawling                ├─ Vector Search                  │
│  ├─ ETL/Preprocessing       ├─ Multi-Query                    │
│  ├─ Chunking                ├─ HyDE                           │
│  ├─ Embedding               └─ Re-ranking                     │
│  └─ Vector Store                                              │
│                                                                 │
│  STAGE 3: GENERATION        STAGE 4: APPLICATION              │
│  ├─ Context Reordering      ├─ RAG Chain                      │
│  ├─ LLM Integration         ├─ FastAPI Backend                │
│  └─ Output Parsing          └─ Next.js Frontend               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Project Structure

```
rag-system/
├── backend/
│   ├── main.py                          # FastAPI entry point
│   ├── config.py                        # Configuration
│   ├── requirements.txt                 # Python dependencies
│   ├── .env.example                     # Environment template
│   ├── core/
│   │   ├── __init__.py
│   │   └── logger.py                    # Logging setup
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health_router.py             # Health check
│   │   ├── indexing_router.py           # Stage 1: Indexing
│   │   ├── retrieval_router.py          # Stage 2: Retrieval
│   │   ├── generation_router.py         # Stage 3: Generation
│   │   └── chat_router.py               # Stage 4: Complete pipeline
│   ├── stage1_indexing/
│   │   ├── __init__.py
│   │   ├── crawling.py                  # Web scraping with cookies
│   │   ├── etl.py                       # PPT/PDF text extraction
│   │   ├── chunking.py                  # Document chunking
│   │   └── embedding.py                 # Embedding generation
│   ├── stage2_retrieval/
│   │   ├── __init__.py
│   │   ├── retriever.py                 # Vector similarity search
│   │   ├── multi_query.py               # Multi-Query generation
│   │   ├── hyde.py                      # HyDE implementation
│   │   └── reranker.py                  # Re-ranking logic
│   ├── stage3_generation/
│   │   ├── __init__.py
│   │   ├── context.py                   # Context reordering (U-Shape)
│   │   ├── llm.py                       # LLM integration (Qwen, Llama)
│   │   └── parser.py                    # Output parsing
│   └── stage4_application/
│       ├── __init__.py
│       └── rag_chain.py                 # LangChain RAG pipeline
├── frontend/
│   ├── package.json                     # Node dependencies
│   ├── tsconfig.json                    # TypeScript config
│   ├── next.config.js                   # Next.js config
│   ├── .env.example                     # Environment template
│   ├── src/
│   │   ├── pages/
│   │   │   ├── _app.tsx                 # App wrapper
│   │   │   ├── _document.tsx            # HTML document
│   │   │   └── index.tsx                # Home page
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx           # Chat UI
│   │   │   ├── MessageList.tsx          # Message display
│   │   │   └── InputArea.tsx            # Input component
│   │   ├── services/
│   │   │   └── api.ts                   # API client
│   │   ├── hooks/
│   │   │   └── useChat.ts               # Chat logic hook
│   │   ├── types/
│   │   │   └── chat.ts                  # TypeScript types
│   │   └── styles/
│   │       └── globals.css              # Global styles
│   └── public/
│       └── favicon.ico
├── docker-compose.yml                   # Docker orchestration
├── .gitignore                           # Git ignore rules
├── .env.example                         # Environment template
├── DEVELOPMENT.md                       # Development guide
└── LICENSE                              # Project license
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose (optional)
- Git

### Local Setup

#### 1. Clone Repository
```bash
git clone https://github.com/nahyud54/rag-system.git
cd rag-system
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configurations

# Run FastAPI server
python main.py
# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

#### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env.local
# Edit .env.local with your API endpoint

# Run development server
npm run dev
# Frontend runs on http://localhost:3000
```

### Docker Setup
```bash
# Build and run all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 4-Stage Pipeline

### Stage 1: Indexing
**Input**: Raw course materials (PPT/PDF files)
**Process**:
1. **Crawling**: Download files from URL with cookies authentication
2. **ETL**: Extract text from PPT/PPTX/PDF → Convert to structured text
3. **Chunking**: Split documents into optimal chunks
4. **Embedding**: Generate embeddings using `paraphrase-multilingual-MiniLM-L12-v2`
5. **Vector Store**: Store embeddings in vector database

**Output**: Indexed and embedded documents

### Stage 2: Retrieval
**Input**: User query
**Process**:
1. **Query Embedding**: Convert query to vector
2. **Similarity Search**: Find top-k relevant documents
3. **Multi-Query**: Generate multiple query variations for better retrieval
4. **HyDE**: Generate hypothetical document to improve search
5. **Re-ranking**: Re-order results using cross-encoder

**Output**: Top relevant documents

### Stage 3: Generation
**Input**: Retrieved context + Original query
**Process**:
1. **Context Reordering**: Arrange documents in U-shape (important at start and end)
2. **Prompt Preparation**: Create optimal prompt template
3. **LLM Generation**: Call LLM (Qwen, Llama 3.2) with context
4. **Output Parsing**: Parse and format LLM output

**Output**: Generated answer

### Stage 4: Application
**Integration**: Complete RAG pipeline with chat interface
- Build complete RAG chain: Query → Retrieval → Prompt → LLM → Output
- Web interface similar to NotebookLM
- Chat history management
- Real-time streaming support

## 🔧 Environment Variables

### Backend (.env)
```
# Server
FAST_API_HOST=0.0.0.0
FAST_API_PORT=8000
DEBUG=True

# LLM
LLM_MODEL=qwen2.5  # or llama2
LLM_API_KEY=your_api_key
LLM_BASE_URL=http://localhost:11434  # For local Ollama

# Embedding
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# Vector Store
VECTOR_DB_TYPE=chroma  # or pinecone, weaviate, etc
VECTOR_DB_PATH=./data/chroma_db

# Retrieval
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.5

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000
```

## 📦 Dependencies

### Backend
- **FastAPI**: Web framework
- **LangChain**: RAG orchestration
- **Sentence-Transformers**: Embedding model
- **ChromaDB/Pinecone**: Vector store
- **python-pptx**: PPT/PPTX extraction
- **PyPDF2**: PDF extraction
- **Pydantic**: Data validation
- **python-dotenv**: Environment management

### Frontend
- **Next.js**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **SWR**: Data fetching
- **Socket.io**: Real-time communication

## 🔑 Key Features

✨ **Indexing**
- Automated web crawling with authentication
- Multi-format document processing (PPT, PDF)
- Intelligent chunking strategies
- Multilingual embedding support

🔍 **Retrieval**
- Vector similarity search
- Multi-Query generation for better recall
- HyDE for hypothetical document expansion
- Cross-encoder re-ranking for precision

🧠 **Generation**
- U-shaped context reordering
- Multiple LLM support (Qwen, Llama)
- Flexible output parsing
- Streaming response support

🌐 **Application**
- Modern chat interface
- Real-time message streaming
- Chat history management
- File upload and processing
- API documentation with Swagger

## 📚 API Endpoints

### Health
- `GET /health` - Health check

### Indexing (Stage 1)
- `POST /api/v1/indexing/crawl` - Crawl and download documents
- `POST /api/v1/indexing/extract` - Extract text from documents
- `POST /api/v1/indexing/chunk` - Chunk documents
- `POST /api/v1/indexing/embed` - Generate embeddings
- `POST /api/v1/indexing/store` - Store in vector database

### Retrieval (Stage 2)
- `POST /api/v1/retrieval/search` - Vector similarity search
- `POST /api/v1/retrieval/multi-query` - Multi-query retrieval
- `POST /api/v1/retrieval/hyde` - HyDE retrieval
- `POST /api/v1/retrieval/rerank` - Re-rank results

### Generation (Stage 3)
- `POST /api/v1/generation/context` - Prepare context
- `POST /api/v1/generation/generate` - Generate answer
- `POST /api/v1/generation/parse` - Parse output

### Chat (Stage 4)
- `POST /api/v1/chat/message` - Send message
- `WebSocket /ws/chat/{session_id}` - Real-time chat
- `GET /api/v1/chat/history/{session_id}` - Get chat history
- `DELETE /api/v1/chat/history/{session_id}` - Clear chat history

## 🚦 Development Workflow

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Make changes** and test locally
3. **Commit**: `git commit -m "Your message"`
4. **Push**: `git push origin feature/your-feature`
5. **Create Pull Request** on GitHub
6. **Review and merge**

See [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed setup instructions.

## 📖 Implementation Roadmap

### Phase 1: Core Infrastructure ✅
- [x] Project structure setup
- [x] FastAPI and Next.js boilerplate
- [x] API routing structure
- [ ] Environment configuration

### Phase 2: Indexing Pipeline
- [ ] Web crawler with authentication
- [ ] Document text extraction
- [ ] Chunking strategies
- [ ] Embedding generation
- [ ] Vector database integration

### Phase 3: Retrieval System
- [ ] Vector similarity search
- [ ] Multi-Query implementation
- [ ] HyDE implementation
- [ ] Re-ranking logic

### Phase 4: Generation Engine
- [ ] Context reordering (U-shape)
- [ ] LLM integration (Qwen, Llama)
- [ ] Output parsing
- [ ] Streaming support

### Phase 5: Application & Deployment
- [ ] RAG chain integration
- [ ] Chat interface development
- [ ] WebSocket implementation
- [ ] Docker containerization
- [ ] Deployment guide

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For issues, questions, or suggestions, please create an issue on GitHub.

## 👤 Author

nahyud54

---

**Happy RAGing! 🚀**
