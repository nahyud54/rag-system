# Development Guide

This document provides detailed instructions for setting up and developing the RAG System.

## Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- pip (Python package manager)
- npm (Node package manager)
- Git
- (Optional) Docker & Docker Compose
- (Optional) CUDA for GPU acceleration

## Backend Development

### 1. Initial Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### 4. Run Backend Server

```bash
# Start FastAPI server
python main.py

# Server will be available at:
# - API: http://localhost:8000
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### 5. Development with Auto-Reload

```bash
# Install uvicorn for development
pip install uvicorn[standard]

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Development

### 1. Initial Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local with your settings
# Make sure NEXT_PUBLIC_API_URL points to your backend
```

### 3. Run Development Server

```bash
# Start Next.js development server
npm run dev

# Frontend will be available at:
# http://localhost:3000
```

### 4. Build for Production

```bash
# Build the project
npm run build

# Start production server
npm start
```

## Docker Development

### Run Everything with Docker Compose

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild images
docker-compose up -d --build
```

### Services Running
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Chroma Vector DB: http://localhost:8000 (internal)

## Database Setup

### Initialize Database

```bash
# Backend/core/db.py automatically initializes SQLite database
# Vector database (Chroma) initializes automatically
```

### View Database

```bash
# SQLite (optional - install sqlite3)
sqlite3 data/rag.db

# Inside sqlite3:
.tables
.schema
SELECT * FROM chat_history;
```

## Testing

### Backend Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_indexing.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
# Install test dependencies
npm install --save-dev jest @testing-library/react

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## Code Style & Linting

### Backend

```bash
# Install linting tools
pip install flake8 black isort mypy

# Format code with black
black .

# Sort imports
isort .

# Check code style
flake8 .

# Type checking
mypy .
```

### Frontend

```bash
# Install linting tools
npm install --save-dev eslint prettier

# Format code
npm run format

# Lint code
npm run lint

# Fix linting issues
npm run lint -- --fix
```

## Common Development Tasks

### Adding a New Endpoint

1. Create a new router file in `backend/routers/`
2. Define your endpoints:
   ```python
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/api/v1/yourfeature", tags=["yourfeature"])
   
   @router.post("/endpoint")
   async def your_endpoint(data: YourModel):
       # Your logic here
       return {"message": "success"}
   ```
3. Import and include in `main.py`:
   ```python
   from routers.yourfeature_router import router as yourfeature_router
   app.include_router(yourfeature_router)
   ```

### Adding a New Page

1. Create a new file in `frontend/src/pages/`
2. Create React component:
   ```tsx
   import React from 'react';
   
   export default function NewPage() {
       return <div>Your page content</div>;
   }
   ```
3. File-based routing automatically creates the route

### Adding Dependencies

**Backend:**
```bash
# Add to requirements.txt and install
pip install package_name
pip freeze > requirements.txt
```

**Frontend:**
```bash
# Add via npm
npm install package_name
# Or with yarn
yarn add package_name
```

## Debugging

### Backend Debugging

```bash
# Add print statements or use pdb
import pdb; pdb.set_trace()

# Or use debugger in VSCode with launch.json configuration
# .vscode/launch.json:
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["main:app", "--reload"],
            "jinja": true,
            "cwd": "${workspaceFolder}/backend"
        }
    ]
}
```

### Frontend Debugging

```bash
# Chrome DevTools available at http://localhost:3000
# Add console.log statements for debugging
# Use React DevTools browser extension

# VSCode debugging:
# .vscode/launch.json:
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "node",
            "request": "launch",
            "name": "Next.js",
            "runtimeExecutable": "npm",
            "runtimeArgs": ["run", "dev"],
            "console": "integratedTerminal"
        }
    ]
}
```

## Environment Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Use different port
uvicorn main:app --reload --port 8001
```

**Virtual environment not activating:**
```bash
# Ensure you're in the backend directory
cd backend
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows
```

**Package installation fails:**
```bash
# Upgrade pip and retry
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Frontend Issues

**Port already in use:**
```bash
# Use different port
npm run dev -- -p 3001
```

**Node modules issues:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Useful Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature-name

# Create Pull Request on GitHub

# After review, merge to main
git checkout main
git pull origin main
git merge feature/your-feature-name
git push origin main
```

## Performance Tips

- Use GPU for embeddings when available (set `EMBEDDING_DEVICE=cuda`)
- Batch embedding generation for better throughput
- Use caching for frequently accessed data
- Implement pagination for large result sets
- Monitor API response times with built-in logging

## Next Steps

1. ✅ Environment is set up
2. 🔄 Start with Stage 1: Indexing implementation
3. 📚 Follow the implementation roadmap in README.md
4. 🧪 Write tests as you develop
5. 📝 Update documentation

---

Happy coding! 🚀
