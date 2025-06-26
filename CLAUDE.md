# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Gemelo Digital**, a conversational AI application that creates a digital twin of "Agustín Modia" with document upload capabilities for contextualized conversations. Built for the Santex Challenge.

## Architecture

The application follows a microservices architecture:
```
Vue.js Frontend → FastAPI Backend → LangGraph Agent → Qdrant Vector DB + OpenAI API
```

**Key Components:**
- **Frontend**: Vue.js 3 with Vite build system
- **Backend**: FastAPI with LangGraph agent orchestration
- **Vector Database**: Qdrant for semantic search
- **AI Services**: OpenAI GPT-4o-mini + text-embedding-3-large
- **Document Processing**: PyPDF2 for PDF parsing and chunking

## Development Commands

**Start Full Stack:**
```bash
# Start all services (frontend, backend, qdrant)
docker-compose up --build

# Access points:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Qdrant Dashboard: http://localhost:6333/dashboard
```

**Backend Development:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Development:**
```bash
cd frontend
npm install
npm run dev        # Dev server with hot reload
npm run build      # Production build
npm run preview    # Preview production build
```

## Configuration

**Required Environment Variables:**
- `OPENAI_API_KEY` - OpenAI API key for LLM and embeddings
- `OPENAI_MODEL=gpt-4o-mini` - OpenAI model (configurable, defaults to gpt-4o-mini)
- `QDRANT_HOST=qdrant` - Vector database host
- `QDRANT_PORT=6333` - Vector database port  
- `COLLECTION_NAME=gemelo_agustin` - Vector collection name

Set these in `.env` file in the root directory.

## Key Architecture Details

**LangGraph Agent System (`/backend/app/agents/gemelo_agent.py`):**
- State-based conversation flow with conditional routing
- Query classification determines when RAG is needed
- Streaming response support for real-time interaction

**Document Processing Pipeline:**
- PDF upload → PyPDF2 parsing → text chunking → embedding generation → Qdrant storage
- Semantic search retrieval during conversations

**Personality System (`/backend/app/prompts/`):**
- Modular prompt files: `system.txt`, `classify.txt`, `router.txt`, `rag.txt`
- Configurable personality traits for "Agustín Modia" digital twin

**API Structure:**
- `/api/chat/` - Conversation endpoints with streaming support
- `/api/documents/` - Document upload and management
- CORS-enabled for frontend integration

## Important File Locations

- **Agent Logic**: `/backend/app/agents/gemelo_agent.py`
- **API Endpoints**: `/backend/app/api/chat.py`, `/backend/app/api/documents.py`  
- **Services**: `/backend/app/services/` (chat, document processing, embeddings, qdrant)
- **Frontend Components**: `/frontend/src/components/` (ChatInterface, DocumentManager, DocumentUpload)
- **Personality Configuration**: `/backend/app/prompts/`

## Testing and Debugging

The application includes comprehensive logging and error handling. Check Docker logs for debugging:
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs qdrant
```

**Development without Docker:**
```bash
# Backend only (requires running Qdrant separately)
cd backend && python -m uvicorn app.main:app --reload

# Frontend only
cd frontend && npm run dev
```

## Vector Database

Qdrant collection `gemelo_agustin` stores document embeddings with metadata filtering support. The service automatically creates the collection with proper indexing on first run.