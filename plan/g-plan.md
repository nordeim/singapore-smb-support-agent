Comprehensive Implementation Plan: Singapore SMB Customer Support AI Agent

Executive Summary

Building a production-ready customer enquiry support AI Agent for Singapore SMBs with:

Frontend: React + TypeScript + Tailwind CSS + Shadcn/UI
Backend: FastAPI + LangChain 1.0 + Pydantic AI
AI: OpenRouter API (GPT-4o models), RAG with multi-stage retrieval
Data: Qdrant (vector DB), Redis (short-term), PostgreSQL (long-term)
Document Ingestion: Microsoft MarkItDown for PDF, DOCX, XLSX, PPTX, HTML, MD, CSV
Channels: WhatsApp Business API + Web Chat with user registration
Deployment: Docker Compose (dev & production)
Phase 1: Deep Analysis & Architecture Validation

1.1 Technology Stack Validation

Component	Technology	Version	Validation Status	Notes
Agent Framework	Pydantic AI + LangChain	Pydantic v1.39.0, LangChain v1.0	✅ Latest stable, API stability guaranteed until 2026	
LLM Provider	OpenRouter API	N/A	✅ Works via OpenAI-compatible API, supports 100+ models	
Vector Database	Qdrant	Latest	✅ Native LangChain integration, hybrid search support	
Reranker	BGE Reranker (local)	bge-reranker-v2-m3	✅ Free, multilingual, integrates via HuggingFaceCrossEncoder	
Embeddings	OpenAI text-embedding-3-small	Latest	✅ Cost-effective, high quality	
Document Parser	Microsoft MarkItDown	Latest	✅ Supports all required formats, produces markdown	
Backend	FastAPI	v0.115+	✅ Async-native, perfect for real-time chat	
Frontend	React 18 + TypeScript	Latest	✅ Modern ecosystem, Shadcn/UI discipline	
WhatsApp	Meta WhatsApp Business API / Twilio	Latest	✅ Both options viable, will implement via webhook	
Memory	Redis + PostgreSQL	Latest	✅ Redis for session (30min TTL), PG for persistence	
1.2 System Architecture

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐         ┌─────────────────────────────────────────────────┐
    │   REACT FRONTEND │         │              BACKEND SERVICES                 │
    │                  │         │  ┌─────────────────────────────────────┐  │
    │ ┌──────────────┐ │         │  │      FASTAPI APPLICATION           │  │
    │ │  Chat Widget  │ │         │  │  ┌───────────────────────────────┐ │  │
    │ │  - Web Chat  │ │◄────────┤  │  │    PYDANTIC AI AGENT        │ │  │
    │ │  - Auth      │ │  REST/   │  │  │                           │ │  │
    │ └──────────────┘ │  WS       │  │  │  System: Singapore SMB support │ │  │
    │                  │          │  │  │  Tools:                    │ │  │
    │ ┌──────────────┐ │          │  │  │  • RAG Retrieval          │ │  │
    │ │ WhatsApp Webhook│ │◄────────┤  │  │  • Customer Lookup       │ │  │
    │ │ Handler        │ │  Webhook  │  │  │  • Business Hours       │ │  │
    │ └──────────────┘ │          │  │  │  • Escalation           │ │  │
    └──────────────────┘         │  │  └─────────┬─────────────────┘ │  │
                              │  │            │                   │  │
                              │  │  ┌─────────▼─────────────────┐ │  │
                              │  │  │      RAG PIPELINE         │ │  │
                              │  │  │  ┌────────────────────┐  │ │  │
                              │  │  │  │  Query Transform │  │ │  │
                              │  │  │  └────────┬────────┘  │ │  │
                              │  │  │           ▼           │ │  │
                              │  │  │  ┌────────────────────┐ │ │  │
                              │  │  │  │  Hybrid Search    │ │ │  │
                              │  │  │  │  (Dense + BM25)  │ │ │  │
                              │  │  │  └────────┬────────┘  │ │  │
                              │  │  │           ▼           │ │  │
                              │  │  │  ┌────────────────────┐ │ │  │
                              │  │  │  │  BGE Reranker    │ │ │  │
                              │  │  │  │  (Local)         │ │ │  │
                              │  │  │  └────────┬────────┘  │ │  │
                              │  │  │           ▼           │ │  │
                              │  │  │  ┌────────────────────┐ │ │  │
                              │  │  │  │  Context Compress│ │ │  │
                              │  │  │  └────────┬────────┘  │ │  │
                              │  │  └───────────┼───────────┘ │  │
                              │  │              │             │  │
                              │  │  ┌─────────────▼─────────────┐ │  │
                              │  │  │    MEMORY LAYER          │ │  │
                              │  │  │  ┌──────────────────┐ │ │  │
                              │  │  │  │  Redis (30min)  │ │ │  │
                              │  │  │  │  Short-term      │ │ │  │
                              │  │  │  └──────────────────┘ │ │  │
                              │  │  │  ┌──────────────────┐ │ │  │
                              │  │  │  │  PostgreSQL      │ │ │  │
                              │  │  │  │  Long-term       │ │ │  │
                              │  │  │  │  PDPA-compliant │ │ │  │
                              │  │  │  └──────────────────┘ │ │  │
                              │  │  └─────────────┼───────────┘ │  │
                              │  │                │             │  │
                              │  │  ┌─────────────▼─────────────┐ │  │
                              │  │  │    KNOWLEDGE LAYER       │ │  │
                              │  │  │  ┌────────────────────┐ │ │  │
                              │  │  │  │     QDRANT        │ │ │  │
                              │  │  │  │  Vector DB       │ │ │  │
                              │  │  │  │  • knowledge     │ │ │  │
                              │  │  │  │  • summaries     │ │ │  │
                              │  │  │  └────────────────────┘ │ │  │
                              │  │  └─────────────────────────┘ │  │
                              │  │                            │  │
                              │  └────────────────────────────┘  │
                              └─────────────────────────────────┘
1.3 Data Flow

USER MESSAGE (Web/WhatsApp)
    │
    ▼
┌─────────────────────────┐
│  FastAPI Endpoint    │
│  POST /api/chat       │
└───────────┬───────────┘
            │
            ▼
┌─────────────────────────┐
│  Load Session from     │
│  Redis (short-term)    │
└───────────┬───────────┘
            │
            ▼
┌─────────────────────────┐
│  Pydantic AI Agent    │
│  - Check intent        │
│  - Route to tools      │
└───────────┬───────────┘
            │
            ├──────────► RAG Retrieval Tool
            │              │
            │              ▼
            │         Query Transform
            │              │
            │              ▼
            │         Hybrid Search (Qdrant)
            │              │
            │              ▼
            │         BGE Reranker (local)
            │              │
            │              ▼
            │         Context Compression
            │              │
            │              └───────────┐
            │                          │
            ▼                          │
┌─────────────────────────┐           │
│  Generate Response    │◄──────────┘
│  (OpenRouter API)    │
└───────────┬───────────┘
            │
            ├──────────► Save to Redis (session)
            │
            ├──────────► Save to PostgreSQL (if summary needed)
            │
            ▼
    STREAM RESPONSE
            │
            ▼
┌─────────────────────────┐
│  Frontend Update     │
│  - Display message    │
│  - Show sources       │
│  - Update typing      │
└─────────────────────────┘
1.4 MarkItDown Integration Design

# Document Ingestion Pipeline Design
from markitdown import MarkItDown

md = MarkItDown()  # Supports: PDF, DOCX, XLSX, PPTX, HTML, MD, CSV

# Conversion flow:
# 1. Parse file → Markdown text
# 2. Extract metadata (author, date, language)
# 3. Semantic chunking (512± tokens)
# 4. Embed with OpenAI text-embedding-3-small
# 5. Store in Qdrant with rich metadata
1.5 OpenRouter Integration Design

# LangChain + OpenRouter Configuration
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="openai/gpt-4o",  # or "openai/gpt-4o-mini"
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": os.getenv("SITE_URL"),
        "X-Title": os.getenv("SITE_NAME"),
    }
)
1.6 BGE Reranker Integration

# Local Reranker with LangChain
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

# Load local model
model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")

# Create reranker compressor
compressor = CrossEncoderReranker(
    model=model,
    top_n=5  # Return top 5 documents
)

# Wrap base retriever
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=qdrant_retriever
)
Phase 2: Project Structure

singapore-smb-support-agent/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app entry
│   │   ├── config.py                    # Pydantic Settings
│   │   ├── dependencies.py              # Dependency injection
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py            # Chat endpoints (REST + WebSocket)
│   │   │   │   ├── auth.py            # Authentication endpoints
│   │   │   │   ├── whatsapp.py        # WhatsApp webhook
│   │   │   │   ├── knowledge.py       # KB management
│   │   │   │   └── health.py          # Health checks
│   │   │   └── websocket.py
│   │   │
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── support_agent.py       # Pydantic AI agent
│   │   │   ├── tools/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── rag_tool.py        # RAG retrieval
│   │   │   │   ├── customer_tool.py   # Customer lookup
│   │   │   │   ├── escalation_tool.py # Human escalation
│   │   │   │   └── business_tool.py   # Hours, policies
│   │   │   ├── prompts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── system.py          # System prompts
│   │   │   │   └── templates.py       # Response templates
│   │   │   └── validators.py          # Response validation
│   │   │
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py            # Main RAG orchestration
│   │   │   ├── retriever.py           # Hybrid retrieval
│   │   │   ├── reranker.py            # BGE reranker
│   │   │   ├── query_transform.py     # Query transformation
│   │   │   └── context_compress.py    # Context compression
│   │   │
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py            # Ingestion orchestrator
│   │   │   ├── parsers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── markitdown_parser.py  # MarkItDown integration
│   │   │   ├── chunkers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── semantic.py        # Semantic chunking
│   │   │   └── embedders/
│   │   │       ├── __init__.py
│   │   │       └── embedding.py       # OpenAI embeddings
│   │   │
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py             # Memory orchestration
│   │   │   ├── short_term.py          # Redis session memory
│   │   │   ├── long_term.py           # PostgreSQL persistence
│   │   │   └── summarizer.py          # Conversation summarization
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py             # Pydantic schemas (API)
│   │   │   ├── domain.py              # Domain models
│   │   │   └── database.py            # SQLAlchemy models
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py        # User operations
│   │   │   ├── conversation_service.py # Conversation operations
│   │   │   └── analytics_service.py   # Usage analytics
│   │   │
│   │   └── integrations/
│   │       ├── __init__.py
│   │       ├── whatsapp.py           # WhatsApp Business API
│   │       └── llm_provider.py       # OpenRouter integration
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   │
│   ├── scripts/
│   │   ├── ingest_documents.py      # Ingestion CLI
│   │   ├── create_samples.py        # Create sample PDFs
│   │   └── seed_knowledge.py       # Initial KB seeding
│   │
│   ├── data/
│   │   ├── samples/                  # Sample documents for testing
│   │   │   ├── sample_faq.pdf
│   │   │   ├── sample_policies.pdf
│   │   │   └── sample_catalog.xlsx
│   │   └── uploads/                  # User-uploaded documents
│   │
│   ├── alembic/                        # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css
│   │   │   └── login/page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                    # Shadcn/UI components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── avatar.tsx
│   │   │   │   ├── scroll-area.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── chat/
│   │   │   │   ├── ChatWidget.tsx       # Main chat container
│   │   │   │   ├── ChatHeader.tsx
│   │   │   │   ├── ChatMessages.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── TypingIndicator.tsx
│   │   │   │   └── QuickReplies.tsx
│   │   │   │
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   │
│   │   │   └── feedback/
│   │   │       ├── FeedbackButton.tsx
│   │   │       └── FeedbackDialog.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useAuth.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── websocket.ts
│   │   │   └── utils.ts
│   │   │
│   │   ├── stores/
│   │   │   ├── chatStore.ts           # Zustand store
│   │   │   └── authStore.ts
│   │   │
│   │   └── types/
│   │       └── index.ts
│   │
│   ├── public/
│   └── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── Dockerfile
│
├── infrastructure/
│   ├── docker-compose.yml             # Local development
│   ├── docker-compose.prod.yml        # Production
│   └── nginx/
│       └── nginx.conf
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── INGESTION_GUIDE.md
│
├── .env.example
├── .gitignore
├── README.md
└── docker-compose.yml
Phase 3: Detailed Implementation Roadmap

Phase 1: Foundation Setup (Days 1-3)

Day 1: Project Initialization

✓ Create repository structure
✓ Initialize Python project (pyproject.toml)
✓ Initialize React + TypeScript + Vite
✓ Configure Tailwind CSS
✓ Initialize Shadcn/UI
✓ Set up Git repository
Key Files:

backend/pyproject.toml: Python dependencies
frontend/package.json: Node.js dependencies
docker-compose.yml: Local dev environment
Dependencies to Install:

# backend/pyproject.toml
[project]
name = "singapore-smb-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "pydantic-ai>=1.39.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-qdrant>=0.2.0",
    "langchain-community>=0.3.0",
    "qdrant-client>=1.12.0",
    "redis>=5.2.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "python-jose>=3.3.0",
    "passlib>=1.7.4",
    "bcrypt>=4.2.0",
    "python-multipart>=0.0.9",
    "markitdown[all]>=0.0.0",
    "sentence-transformers>=3.3.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "black>=24.10.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]
// frontend/package.json
{
  "name": "smb-support-agent-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.0",
    "lucide-react": "^0.462.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.3",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.15.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.14",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.15",
    "typescript": "~5.6.0",
    "vite": "^6.0.3"
  }
}
Day 2: Database & Vector Store Setup

✓ PostgreSQL schema design
✓ SQLAlchemy models
✓ Alembic migrations
✓ Redis connection config
✓ Qdrant collection setup
✓ Database seeding scripts
Database Schema:

-- users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),  -- For WhatsApp integration
    whatsapp_number VARCHAR(50),  -- Linked WhatsApp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    pdpa_consent_given BOOLEAN DEFAULT FALSE,
    pdpa_consent_date TIMESTAMP
);

-- conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,  -- 'web', 'whatsapp'
    external_session_id VARCHAR(255),  -- WhatsApp phone number
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'  -- 'active', 'closed', 'escalated'
);

-- messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT,  -- LLM confidence score
    requires_escalation BOOLEAN DEFAULT FALSE,
    is_summarized BOOLEAN DEFAULT FALSE
);

-- conversation_summaries table
CREATE TABLE conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    summary_type VARCHAR(50),  -- 'daily', 'session', 'key_points'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- support_tickets table (for escalation)
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(50) DEFAULT 'normal',
    subject TEXT,
    description TEXT,
    escalation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    assigned_to VARCHAR(255)  -- Human agent identifier
);
Qdrant Collections:

# knowledge collection
knowledge_collection = {
    "name": "knowledge_base",
    "vectors": {
        "size": 1536,  # text-embedding-3-small dimension
        "distance": "Cosine"
    },
    "payload_schema": {
        "source": "keyword",
        "category": "keyword",
        "language": "keyword",
        "file_name": "keyword",
        "chunk_index": "integer",
        "created_at": "text",
        "confidence_score": "float"
    }
}

# summaries collection
summaries_collection = {
    "name": "conversation_summaries",
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload_schema": {
        "conversation_id": "keyword",
        "summary_type": "keyword",
        "created_at": "text"
    }
}
Day 3: Docker Compose Setup

# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: smb_agent
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/smb_agent
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_started
    volumes:
      - ./backend:/app
      - ./backend/data:/app/data

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  qdrant_data:
Phase 2: Document Ingestion Pipeline (Days 4-6)

Day 4: MarkItDown Integration

# backend/app/ingestion/parsers/markitdown_parser.py
from markitdown import MarkItDown
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MarkItDownParser:
    """
    Document parser using Microsoft's MarkItDown library.
    Supports: PDF, DOCX, XLSX, PPTX, HTML, MD, CSV
    """
    
    def __init__(self):
        self.md = MarkItDown()
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse document and extract content with metadata.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with text_content, metadata
        """
        try:
            logger.info(f"Parsing file: {file_path}")
            result = self.md.convert(file_path)
            
            # Extract file metadata
            path = Path(file_path)
            metadata = {
                "source": str(path),
                "file_name": path.name,
                "file_extension": path.suffix.lower(),
                "file_size": path.stat().st_size if path.exists() else 0,
            }
            
            # Add MarkItDown metadata if available
            if hasattr(result, 'metadata'):
                metadata.update(result.metadata)
            
            return {
                "text_content": result.text_content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            raise
Usage:

parser = MarkItDownParser()

# Parse different file types
result_pdf = parser.parse("backend/data/sample_faq.pdf")
result_docx = parser.parse("backend/data/policy.docx")
result_xlsx = parser.parse("backend/data/catalog.xlsx")
result_html = parser.parse("backend/data/index.html")
Day 5: Semantic Chunking & Metadata

# backend/app/ingestion/chunkers/semantic.py
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticChunker:
    """
    Semantic chunking using sentence embeddings.
    Splits at semantic boundaries based on cosine similarity.
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 target_chunk_size: int = 512,
                 threshold: float = 0.5):
        """
        Args:
            model_name: Sentence transformer model
            target_chunk_size: Target token count (±100)
            threshold: Cosine similarity threshold for split
        """
        self.model = SentenceTransformer(model_name)
        self.target_chunk_size = target_chunk_size
        self.threshold = threshold
    
    def chunk(self, 
             text: str, 
             metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into semantic chunks.
        
        Args:
            text: Full document text
            metadata: Document metadata to attach to all chunks
            
        Returns:
            List of chunks with text and enriched metadata
        """
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        if len(sentences) == 0:
            return [{"text": text, "metadata": metadata}]
        
        # Get embeddings
        embeddings = self.model.encode(sentences)
        
        # Build chunks based on semantic similarity
        chunks = []
        current_chunk = []
        
        for i, sentence in enumerate(sentences):
            if not current_chunk:
                current_chunk.append(sentence)
                continue
            
            # Calculate similarity with last sentence in chunk
            last_embedding = embeddings[i-1]
            current_embedding = embeddings[i]
            similarity = self._cosine_similarity(
                last_embedding, 
                current_embedding
            )
            
            # Split if similarity is below threshold or chunk is too large
            if similarity < self.threshold or self._estimate_tokens(
                "\n".join(current_chunk + [sentence])
            ) > self.target_chunk_size + 100:
                # Save current chunk
                chunks.append({
                    "text": "\n".join(current_chunk),
                    "metadata": {
                        **metadata,
                        "chunk_index": len(chunks)
                    }
                })
                current_chunk = [sentence]
            else:
                current_chunk.append(sentence)
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append({
                "text": "\n".join(current_chunk),
                "metadata": {
                    **metadata,
                    "chunk_index": len(chunks)
                }
            })
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting (can be enhanced)."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token)."""
        return len(text) // 4
Day 6: Embedding & Qdrant Upsert

# backend/app/ingestion/embedders/embedding.py
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """
    Manage embeddings and Qdrant operations.
    Uses OpenAI text-embedding-3-small.
    """
    
    def __init__(self):
        # OpenRouter-compatible OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        
        # Qdrant client
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333")
        )
        
        self.collection_name = "knowledge_base"
    
    async def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Embed chunks and upsert to Qdrant.
        
        Args:
            chunks: List of chunks with text and metadata
        """
        try:
            logger.info(f"Upserting {len(chunks)} chunks to Qdrant")
            
            # Create collection if not exists
            self._ensure_collection()
            
            # Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.embeddings.aembed_documents(texts)
            
            # Create points
            points = [
                PointStruct(
                    id=f"{chunk['metadata']['file_name']}-{i}",
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        **chunk["metadata"]
                    }
                )
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
            ]
            
            # Batch upsert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                batch_size=100
            )
            
            logger.info(f"Successfully upserted {len(points)} points")
            
        except Exception as e:
            logger.error(f"Error upserting chunks: {e}")
            raise
    
    def _ensure_collection(self):
        """Ensure Qdrant collection exists."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            logger.info(f"Creating collection {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # text-embedding-3-small
                    distance=Distance.COSINE
                )
            )
Phase 3: RAG Pipeline (Days 7-10)

Day 7: Query Transformation

# backend/app/rag/query_transform.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class QueryTransformer:
    """
    Transform user queries for better retrieval.
    Includes rewriting, intent classification, language detection.
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.transform_prompt = ChatPromptTemplate.from_template("""
        You are a query transformation expert for a Singapore SMB customer support system.
        
        Original Query: {query}
        
        Your task:
        1. Rewrite the query to be clearer and more specific
        2. Identify the intent (product_info, pricing, hours, policy, other)
        3. Detect the language (en, zh, ms, ta)
        
        Output format (JSON):
        {{
            "rewritten_query": "clearer version",
            "intent": "intent_category",
            "language": "language_code"
        }}
        """)
    
    async def transform(self, query: str) -> Dict[str, str]:
        """
        Transform the user query.
        
        Args:
            query: Original user query
            
        Returns:
            Dictionary with rewritten_query, intent, language
        """
        try:
            response = await self.llm.ainvoke(
                self.transform_prompt.format(query=query)
            )
            
            import json
            return json.loads(response.content)
            
        except Exception as e:
            logger.error(f"Error transforming query: {e}")
            # Fallback to original query
            return {
                "rewritten_query": query,
                "intent": "general",
                "language": "en"
            }
Day 8: Hybrid Retrieval (Qdrant)

# backend/app/rag/retriever.py
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import MergerRetriever
from langchain_community.retrievers import BM25Retriever
from qdrant_client import QdrantClient
from typing import List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Hybrid retrieval combining dense vector search and sparse BM25.
    Uses Reciprocal Rank Fusion (RRF) for merging.
    """
    
    def __init__(self):
        # OpenRouter-compatible embeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            base_url=os.getenv("OPENROUTER_BASE_URL"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        
        # Qdrant client
        client = QdrantClient(url=os.getenv("QDRANT_URL"))
        
        # Dense retriever (vector search)
        self.dense_retriever = QdrantVectorStore(
            client=client,
            collection_name="knowledge_base",
            embedding=embeddings
        ).as_retriever(
            search_kwargs={"k": 20}  # Get top 20 for reranking
        )
        
        # Sparse retriever (BM25) - for keyword search
        # Note: BM25 requires indexed documents, will implement with separate index
        self.sparse_retriever = None  # Can be added with langchain-community
        
        # Merge retrievers (RRF)
        if self.sparse_retriever:
            self.hybrid_retriever = MergerRetriever(
                retrievers=[self.dense_retriever, self.sparse_retriever]
            )
        else:
            self.hybrid_retriever = self.dense_retriever
        
        logger.info("Hybrid retriever initialized")
    
    async def retrieve(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents.
        
        Args:
            query: Transformed query
            top_k: Number of documents to retrieve
            
        Returns:
            List of documents with scores
        """
        try:
            docs = await self.hybrid_retriever.ainvoke(query)
            
            # Limit to top_k
            return docs[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
Day 9: BGE Reranking (Local)

# backend/app/rag/reranker.py
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from typing import List
import logging

logger = logging.getLogger(__name__)

class BGEReranker:
    """
    Local reranker using BGE models.
    Cross-encoder for precise document relevance scoring.
    """
    
    def __init__(self, 
                 model_name: str = "BAAI/bge-reranker-v2-m3",
                 top_n: int = 5,
                 device: str = "cpu"):
        """
        Args:
            model_name: HuggingFace model name or local path
            top_n: Number of top documents to return
            device: 'cpu' or 'cuda' if available
        """
        logger.info(f"Loading BGE reranker: {model_name}")
        
        self.model = HuggingFaceCrossEncoder(
            model_name=model_name,
            model_kwargs={"device": device}
        )
        
        self.compressor = CrossEncoderReranker(
            model=self.model,
            top_n=top_n
        )
        
        self.top_n = top_n
        logger.info(f"BGE reranker loaded, returning top {top_n} documents")
    
    async def rerank(self, 
                   query: str, 
                   documents: List[Any]) -> List[Any]:
        """
        Rerank documents based on query relevance.
        
        Args:
            query: User query
            documents: Retrieved documents from hybrid search
            
        Returns:
            Reranked top-n documents
        """
        if not documents:
            return []
        
        try:
            logger.info(f"Reranking {len(documents)} documents")
            
            # Create compression retriever
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=self.compressor,
                base_retriever=MockRetriever(documents)
            )
            
            # Rerank
            reranked = await compression_retriever.ainvoke(query)
            
            return reranked
            
        except Exception as e:
            logger.error(f"Error reranking documents: {e}")
            # Fallback: return original top-n
            return documents[:self.top_n]


class MockRetriever:
    """Helper for reranking base retriever."""
    
    def __init__(self, documents: List[Any]):
        self.documents = documents
    
    async def ainvoke(self, query: str) -> List[Any]:
        return self.documents
Day 10: Context Compression & Assembly

# backend/app/rag/context_compress.py
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ContextCompressor:
    """
    Compress retrieved context to fit within token budget.
    Uses extractive compression (keep relevant sentences).
    """
    
    def __init__(self, max_tokens: int = 4000):
        """
        Args:
            max_tokens: Maximum tokens for context
        """
        self.max_tokens = max_tokens
    
    def compress(self, 
               query: str, 
               documents: List[Dict[str, Any]]) -> str:
        """
        Compress documents into context string.
        
        Args:
            query: User query
            documents: Reranked documents
            
        Returns:
            Compressed context string
        """
        if not documents:
            return ""
        
        # Extractive: Just concatenate top documents
        context_parts = []
        current_tokens = 0
        
        for i, doc in enumerate(documents):
            doc_text = doc.page_content if hasattr(doc, 'page_content') else doc.get('text', '')
            source = doc.metadata.get('source', 'unknown') if hasattr(doc, 'metadata') else doc.get('metadata', {}).get('source', 'unknown')
            
            # Estimate tokens
            doc_tokens = len(doc_text) // 4  # Rough estimate
            
            if current_tokens + doc_tokens > self.max_tokens:
                # Partial document or stop
                remaining = self.max_tokens - current_tokens
                partial_text = doc_text[:remaining * 4]
                context_parts.append(f"[Source: {source}]\n{partial_text}...")
                break
            
            context_parts.append(f"[Source: {source}]\n{doc_text}")
            current_tokens += doc_tokens
        
        return "\n\n".join(context_parts)
Phase 4: Memory System (Days 11-13)

Day 11: Short-term Memory (Redis)

# backend/app/memory/short_term.py
from redis import asyncio as aioredis
from typing import List, Dict, Any, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)

class ShortTermMemory:
    """
    Redis-based session memory.
    Stores conversation history with 30-minute TTL.
    """
    
    def __init__(self):
        self.redis = aioredis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            encoding="utf-8",
            decode_responses=True
        )
        self.session_prefix = "session:"
        self.ttl = 1800  # 30 minutes
    
    async def save_message(self, 
                        session_id: str, 
                        role: str, 
                        content: str,
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Save a message to session history.
        
        Args:
            session_id: Unique session identifier
            role: 'user', 'assistant', or 'system'
            content: Message content
            metadata: Additional metadata (confidence, sources, etc.)
        """
        try:
            key = f"{self.session_prefix}{session_id}"
            
            message = {
                "role": role,
                "content": content,
                "timestamp": str(asyncio.get_event_loop().time()),
                **(metadata or {})
            }
            
            # Add to Redis list
            await self.redis.lpush(key, json.dumps(message))
            
            # Set TTL on first message or reset
            await self.redis.expire(key, self.ttl)
            
            logger.debug(f"Saved message to session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
    
    async def get_history(self, 
                       session_id: str, 
                       limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages (default: all)
            
        Returns:
            List of messages in chronological order (oldest first)
        """
        try:
            key = f"{self.session_prefix}{session_id}"
            
            # Get all messages
            messages_raw = await self.redis.lrange(key, 0, -1)
            
            # Parse JSON
            messages = [
                json.loads(msg) 
                for msg in messages_raw
            ]
            
            # Reverse to get chronological order
            messages.reverse()
            
            if limit:
                messages = messages[-limit:]
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    async def clear_session(self, session_id: str):
        """Clear session history."""
        try:
            key = f"{self.session_prefix}{session_id}"
            await self.redis.delete(key)
            logger.info(f"Cleared session {session_id}")
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
    
    async def get_message_count(self, session_id: str) -> int:
        """Get count of messages in session."""
        try:
            key = f"{self.session_prefix}{session_id}"
            return await self.redis.llen(key)
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0
Day 12: Long-term Memory (PostgreSQL)

# backend/app/memory/long_term.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.database import Message, ConversationSummary
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LongTermMemory:
    """
    PostgreSQL-based persistent memory.
    Stores conversation summaries and historical data.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save_summary(self,
                         conversation_id: str,
                         summary: str,
                         summary_type: str = "session"):
        """
        Save conversation summary.
        
        Args:
            conversation_id: Conversation UUID
            summary: Generated summary text
            summary_type: 'session', 'daily', 'key_points'
        """
        try:
            db_summary = ConversationSummary(
                conversation_id=conversation_id,
                summary=summary,
                summary_type=summary_type
            )
            
            self.db.add(db_summary)
            await self.db.commit()
            
            logger.info(f"Saved {summary_type} summary for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            await self.db.rollback()
    
    async def get_recent_summaries(self,
                                 conversation_id: str,
                                 limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent summaries for a conversation."""
        try:
            result = await self.db.execute(
                select(ConversationSummary)
                .where(ConversationSummary.conversation_id == conversation_id)
                .order_by(ConversationSummary.created_at.desc())
                .limit(limit)
            )
            
            summaries = result.scalars().all()
            
            return [
                {
                    "id": str(s.id),
                    "summary": s.summary,
                    "type": s.summary_type,
                    "created_at": s.created_at.isoformat()
                }
                for s in summaries
            ]
            
        except Exception as e:
            logger.error(f"Error getting summaries: {e}")
            return []
    
    async def create_support_ticket(self,
                                 conversation_id: str,
                                 user_id: str,
                                 subject: str,
                                 description: str,
                                 escalation_reason: str):
        """Create escalation ticket."""
        from app.models.database import SupportTicket
        import uuid
        
        try:
            ticket = SupportTicket(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                user_id=user_id,
                status="open",
                priority="normal",
                subject=subject,
                description=description,
                escalation_reason=escalation_reason
            )
            
            self.db.add(ticket)
            await self.db.commit()
            
            logger.info(f"Created ticket {ticket.id} for escalation")
            return ticket.id
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await self.db.rollback()
            raise
Day 13: Memory Manager & Summarization

# backend/app/memory/manager.py
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.memory.summarizer import ConversationSummarizer
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Orchestrate memory operations.
    Manages short-term, long-term, and summarization.
    """
    
    def __init__(self, 
                 redis_client: ShortTermMemory,
                 db_session,
                 llm: ChatOpenAI):
        self.short_term = redis_client
        self.long_term = LongTermMemory(db_session)
        self.summarizer = ConversationSummarizer(llm)
        self.max_messages = 20  # Summarize after 20 messages
    
    async def add_message(self,
                        session_id: str,
                        role: str,
                        content: str,
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Add message and check if summarization is needed.
        """
        # Save to Redis
        await self.short_term.save_message(
            session_id, role, content, metadata
        )
        
        # Check message count
        count = await self.short_term.get_message_count(session_id)
        
        if count >= self.max_messages:
            logger.info(f"Session {session_id} has {count} messages, triggering summarization")
            await self._summarize_and_compress(session_id)
    
    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get context for LLM call.
        Combines recent messages and summaries.
        """
        # Get recent messages (last 5)
        recent = await self.short_term.get_history(session_id, limit=5)
        
        # Get summaries from long-term memory
        # (would need conversation_id mapping)
        summaries = []  # Placeholder
        
        return {
            "recent_messages": recent,
            "summaries": summaries
        }
    
    async def _summarize_and_compress(self, session_id: str):
        """Summarize old messages and store summary."""
        # Get all messages
        messages = await self.short_term.get_history(session_id)
        
        if len(messages) <= 5:
            return
        
        # Keep last 5, summarize the rest
        to_summarize = messages[:-5]
        recent = messages[-5:]
        
        # Generate summary
        summary = await self.summarizer.summarize(
            to_summarize,
            summary_type="session"
        )
        
        # Store in long-term memory
        # (would need conversation_id)
        # await self.long_term.save_summary(...)
        
        # Replace old messages in Redis with recent + summary marker
        await self.short_term.clear_session(session_id)
        
        # Add summary as system message
        await self.short_term.save_message(
            session_id,
            "system",
            f"[Previous session summary]: {summary}"
        )
        
        # Add back recent messages
        for msg in recent:
            await self.short_term.save_message(
                session_id,
                msg["role"],
                msg["content"],
                msg.get("metadata")
            )
Phase 5: Pydantic AI Agent (Days 14-17)

Day 14: Agent Definition

# backend/app/agent/support_agent.py
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Result schema
class SupportResponse(BaseModel):
    """Structured output for support agent."""
    message: str
    confidence: float = 0.0
    sources: List[str] = []
    suggested_actions: List[str] = []
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None

# Dependencies for agent
@dataclass
class SupportDependencies:
    """Dependencies injected into agent."""
    rag_retriever: "RAGPipeline"
    customer_service: "CustomerService"
    memory_manager: "MemoryManager"
    business_context: "BusinessContext"

# Agent definition
support_agent = Agent[SupportDependencies, SupportResponse](
    name="singapore_smb_support",
    model="openai/gpt-4o",  # Will use OpenRouter
    
    system_prompt=(
        "You are a customer support specialist for Singapore SMBs. "
        "You handle enquiries for retail, F&B, and service businesses. "
        "Be professional, friendly, and culturally aware. "
        "Always provide accurate information from your knowledge base. "
        "If you're unsure, acknowledge uncertainty and offer to escalate to a human. "
        "PDPA Compliance: "
        "- Never collect or store personal data without consent "
        "- Handle queries professionally "
        "- Respect data minimization principles"
    ),
    
    deps_type=SupportDependencies,
    result_type=SupportResponse,
    
    # Add tools
    tools=[
        "retrieve_knowledge",
        "get_customer_info",
        "check_business_hours",
        "create_support_ticket",
        "escalate_to_human"
    ]
)

# Dynamic instructions
@support_agent.instructions
async def add_business_context(ctx: RunContext[SupportDependencies]) -> str:
    """Add business-specific context to system prompt."""
    context = await ctx.deps.business_context.get_context()
    return f"""
    
    Business Context:
    - Business Type: {context['business_type']}
    - Operating Hours: {context['hours']}
    - Services: {', '.join(context['services'])}
    - Location: {context['location']}
    """

# Tool: RAG Retrieval
@support_agent.tool
async def retrieve_knowledge(
    ctx: RunContext[SupportDependencies],
    query: str
) -> str:
    """Retrieve relevant information from knowledge base."""
    try:
        # Transform query
        transformed = await ctx.deps.rag_retriever.transform_query(query)
        
        # Retrieve documents
        docs = await ctx.deps.rag_retriever.retrieve(
            transformed['rewritten_query']
        )
        
        # Rerank
        docs = await ctx.deps.rag_retriever.rerank(query, docs)
        
        # Compress context
        context = ctx.deps.rag_retriever.compress_context(query, docs)
        
        return f"Retrieved Context:\n{context}"
        
    except Exception as e:
        logger.error(f"Error retrieving knowledge: {e}")
        return "No relevant information found in knowledge base."

# Tool: Customer Info
@support_agent.tool
async def get_customer_info(
    ctx: RunContext[SupportDependencies],
    customer_id: str
) -> str:
    """Get customer information from database."""
    try:
        customer = await ctx.deps.customer_service.get_customer(customer_id)
        if customer:
            return f"Customer: {customer['full_name']}, Email: {customer['email']}"
        return "Customer not found."
    except Exception as e:
        logger.error(f"Error getting customer: {e}")
        return "Error retrieving customer information."

# Tool: Business Hours
@support_agent.tool
async def check_business_hours(ctx: RunContext[SupportDependencies]) -> str:
    """Check current business hours status."""
    from datetime import datetime
    import pytz
    
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz)
    
    hours = await ctx.deps.business_context.get_hours()
    # Implement business hours logic
    is_open = hours['is_open'](now)
    
    status = "OPEN" if is_open else "CLOSED"
    return f"Business is currently {status}. Hours: {hours['display']}"

# Tool: Create Support Ticket
@support_agent.tool
async def create_support_ticket(
    ctx: RunContext[SupportDependencies],
    user_id: str,
    subject: str,
    description: str
) -> str:
    """Create a support ticket for escalation."""
    try:
        ticket_id = await ctx.deps.memory_manager.create_ticket(
            user_id=user_id,
            subject=subject,
            description=description
        )
        return f"Support ticket {ticket_id} created. A human agent will assist you shortly."
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        return "Error creating support ticket."

# Tool: Escalate to Human
@support_agent.tool
async def escalate_to_human(
    ctx: RunContext[SupportDependencies],
    reason: str,
    conversation_id: str
) -> str:
    """Escalate conversation to human agent."""
    try:
        await ctx.deps.customer_service.escalate(
            conversation_id=conversation_id,
            reason=reason
        )
        return "Connecting you to a human agent..."
    except Exception as e:
        logger.error(f"Error escalating: {e}")
        return "Error escalating to human. Please try again."
Day 15-16: Tool Implementations

# backend/app/agent/tools/rag_tool.py
from app.rag.pipeline import RAGPipeline
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class RAGTool:
    """RAG retrieval tool for agent."""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag = rag_pipeline
    
    async def retrieve(self, query: str) -> Dict[str, any]:
        """Execute full RAG pipeline."""
        try:
            # Step 1: Query transformation
            transformed = await self.rag.transform_query(query)
            
            # Step 2: Hybrid retrieval
            docs = await self.rag.retrieve(
                transformed['rewritten_query'],
                top_k=20
            )
            
            # Step 3: Reranking
            docs = await self.rag.rerank(query, docs)
            
            # Step 4: Context compression
            context = self.rag.compress_context(query, docs)
            
            return {
                "context": context,
                "sources": [d.metadata.get('source') for d in docs if hasattr(d, 'metadata')],
                "confidence": 0.85  # Placeholder, calculate from reranker scores
            }
            
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return {
                "context": "",
                "sources": [],
                "confidence": 0.0
            }
Phase 6: API Layer (Days 18-20)

Day 18: Chat REST Endpoints

# backend/app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from app.models.schemas import ChatRequest, ChatResponse
from app.dependencies import get_current_user, get_memory_manager
from app.agent.support_agent import support_agent, SupportDependencies
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    memory_manager = Depends(get_memory_manager)
):
    """
    Handle chat message (REST endpoint).
    Returns structured response with streaming option.
    """
    try:
        # Save user message to memory
        await memory_manager.add_message(
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        
        # Prepare dependencies
        deps = SupportDependencies(
            rag_retriever=request.app.state.rag_pipeline,
            customer_service=request.app.state.customer_service,
            memory_manager=memory_manager,
            business_context=request.app.state.business_context
        )
        
        # Run agent
        result = await support_agent.run(
            user_message=request.message,
            deps=deps
        )
        
        # Save assistant response to memory
        await memory_manager.add_message(
            session_id=request.session_id,
            role="assistant",
            content=result.output.message,
            metadata={
                "confidence": result.output.confidence,
                "sources": result.output.sources
            }
        )
        
        return ChatResponse(
            message=result.output.message,
            confidence=result.output.confidence,
            sources=result.output.sources,
            requires_escalation=result.output.requires_escalation,
            suggested_actions=result.output.suggested_actions
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Error processing message")

@router.websocket("/ws/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming responses.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process with agent
            # Stream chunks back
            # (implementation details)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
Day 19: Authentication

# backend/app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.schemas import UserCreate, UserLogin, Token
from app.services.user_service import UserService
from app.dependencies import get_db
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/register", response_model=Token)
async def register(
    user: UserCreate,
    db = Depends(get_db)
):
    """Register new user."""
    try:
        # Check if user exists
        user_service = UserService(db)
        existing = await user_service.get_by_email(user.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Create user
        new_user = await user_service.create(
            email=user.email,
            password=user.password,
            full_name=user.full_name
        )
        
        # Generate token
        access_token = create_access_token(data={"sub": new_user.email})
        
        return Token(access_token=access_token, token_type="bearer")
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db = Depends(get_db)):
    """Login user and return JWT token."""
    try:
        user_service = UserService(db)
        user = await user_service.authenticate(
            credentials.username,
            credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Generate token
        access_token = create_access_token(data={"sub": user.email})
        
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

def create_access_token(data: dict):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )
    
    return encoded_jwt
Day 20: WhatsApp Integration

# backend/app/api/routes/whatsapp.py
from fastapi import APIRouter, Request, HTTPException
from app.integrations.whatsapp import WhatsAppClient
from app.agent.support_agent import support_agent, SupportDependencies
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp messages from Meta API.
    """
    try:
        data = await request.json()
        
        # Verify webhook (skip for brevity)
        
        # Process messages
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        for message in change['value'].get('messages', []):
                            await _process_whatsapp_message(message)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")

async def _process_whatsapp_message(message: dict):
    """Process individual WhatsApp message."""
    try:
        # Extract message details
        phone_number = message['from']
        text = message['text']['body']
        
        # Get or create conversation
        # Use phone number as external_session_id
        
        # Process with agent
        # Same logic as web chat
        
        # Send response via WhatsApp API
        await whatsapp_client.send_message(
            phone_number=phone_number,
            text=response
        )
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")
Phase 7: Frontend Development (Days 21-26)

Day 21: Shadcn/UI Setup

# Install Shadcn/UI
npx shadcn-ui@latest init

# Add required components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add scroll-area
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add badge
Day 22: Chat Widget Component

// frontend/src/components/chat/ChatWidget.tsx
import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useChatStore } from '@/stores/chatStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Send, Bot, User } from 'lucide-react';

export function ChatWidget() {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  const { messages, sendMessage, isConnected } = useChatStore();
  const { send, lastMessage, ready } = useWebSocket(
    `ws://localhost:8000/api/chat/ws/${session_id}`
  );

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', content: input, timestamp: new Date() };
    sendMessage(userMsg);
    setInput('');
    setIsTyping(true);

    // Send via WebSocket or REST
    if (ready) {
      send(JSON.stringify({ message: input }));
    } else {
      // Fallback to REST
      await sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-[600px] w-full max-w-2xl border rounded-lg">
      {/* Header */}
      <div className="p-4 border-b bg-muted">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          <h2 className="font-semibold">SMB Support Assistant</h2>
          <Badge variant={isConnected ? 'default' : 'destructive'}>
            {isConnected ? 'Online' : 'Offline'}
          </Badge>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} message={msg} />
        ))}
        {isTyping && <TypingIndicator />}
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            disabled={!isConnected}
          />
          <Button onClick={handleSend} disabled={!isConnected}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
Day 23: Authentication Forms

// frontend/src/components/auth/LoginForm.tsx
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuthStore } from '@/stores/authStore';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      await login(email, password);
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
      <Button type="submit" className="w-full">
        Login
      </Button>
    </form>
  );
}
Phase 8: Testing & Sample Data (Days 27-30)

Day 27-28: Sample Document Generation

# backend/scripts/create_samples.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document
from openpyxl import Workbook
from pptx import Presentation
import os

def create_sample_faq():
    """Create sample FAQ PDF."""
    c = canvas.Canvas("backend/data/samples/sample_faq.pdf", pagesize=letter)
    
    content = """
    FREQUENTLY ASKED QUESTIONS - Singapore SMB Support
    
    Q1: What are your business hours?
    A: We are open Monday to Friday, 9:00 AM to 6:00 PM Singapore time.
        We are closed on weekends and public holidays.
    
    Q2: Do you offer delivery services?
    A: Yes, we offer islandwide delivery in Singapore for orders above $50.
        Delivery fee is $5 for orders below $100, free for orders above $100.
    
    Q3: What payment methods do you accept?
    A: We accept PayNow, Visa/Mastercard, GrabPay, and cash on delivery.
    
    Q4: How can I track my order?
    A: You will receive a tracking link via SMS and email once your order is dispatched.
    
    Q5: What is your return policy?
    A: We accept returns within 14 days of purchase with original receipt.
        Items must be unused and in original packaging.
    """
    
    textobject = c.beginText()
    textobject.setTextOrigin(50, 750)
    textobject.textLines(content.split('\n'))
    c.drawTextObject(textobject)
    c.save()

def create_sample_policies():
    """Create sample policy document."""
    doc = Document()
    
    doc.add_heading('Business Policies', 0)
    
    doc.add_heading('Privacy Policy (PDPA Compliant)', 1)
    doc.add_paragraph(
        'We are committed to protecting your personal data in accordance with '
        'Singapore\'s Personal Data Protection Act (PDPA).'
    )
    doc.add_paragraph('We collect, use, and disclose your personal data only:')
    doc.add_paragraph('1. For purposes you have consented to', style='List Bullet')
    doc.add_paragraph('2. To provide the services you request', style='List Bullet')
    doc.add_paragraph('3. To comply with legal obligations', style='List Bullet')
    
    doc.add_heading('Data Retention', 1)
    doc.add_paragraph(
        'We retain personal data only as long as necessary for the purposes '
        'for which it was collected, unless required or permitted by law to retain longer.'
    )
    
    doc.save('backend/data/samples/sample_policies.docx')

def create_sample_catalog():
    """Create sample product catalog."""
    wb = Workbook()
    ws = wb.active
    
    ws.title = "Product Catalog"
    
    # Headers
    headers = ['Product ID', 'Name', 'Category', 'Price (SGD)', 'Stock', 'Description']
    ws.append(headers)
    
    # Sample products
    products = [
        ['P001', 'Wireless Earbuds', 'Electronics', 49.90, 150, 'High-quality wireless earbuds with noise cancellation'],
        ['P002', 'Premium Coffee Beans', 'F&B', 25.00, 80, 'Singapore-roasted premium arabica beans'],
        ['P003', 'Desk Lamp', 'Home', 35.00, 45, 'LED desk lamp with adjustable brightness'],
        ['P004', 'Organic Rice', 'F&B', 18.50, 200, 'Premium organic rice (5kg bag)'],
        ['P005', 'Phone Stand', 'Electronics', 15.90, 120, 'Adjustable aluminum phone stand'],
    ]
    
    for product in products:
        ws.append(product)
    
    wb.save('backend/data/samples/sample_catalog.xlsx')

if __name__ == '__main__':
    os.makedirs('backend/data/samples', exist_ok=True)
    
    print("Creating sample documents...")
    create_sample_faq()
    create_sample_policies()
    create_sample_catalog()
    
    print("Sample documents created in backend/data/samples/")
Day 29: Ingestion Script

# backend/scripts/ingest_documents.py
import asyncio
from app.ingestion.parsers.markitdown_parser import MarkItDownParser
from app.ingestion.chunkers.semantic import SemanticChunker
from app.ingestion.embedders.embedding import EmbeddingManager
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Ingest all documents from data/samples directory."""
    
    # Initialize components
    parser = MarkItDownParser()
    chunker = SemanticChunker()
    embedder = EmbeddingManager()
    
    samples_dir = Path("backend/data/samples")
    
    for file_path in samples_dir.glob("*"):
        logger.info(f"Processing {file_path.name}...")
        
        try:
            # Parse document
            result = parser.parse(str(file_path))
            
            # Extract metadata
            metadata = result["metadata"]
            metadata.update({
                "category": "faq" if "faq" in file_path.name.lower() else 
                           "policies" if "policy" in file_path.name.lower() else 
                           "products",
                "language": "en",
                "created_at": "2025-01-01"
            })
            
            # Chunk text
            chunks = chunker.chunk(result["text_content"], metadata)
            
            # Embed and upsert
            await embedder.upsert_chunks(chunks)
            
            logger.info(f"Ingested {len(chunks)} chunks from {file_path.name}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
    
    logger.info("Ingestion complete!")

if __name__ == '__main__':
    asyncio.run(main())
Day 30: Testing & Validation

# backend/tests/integration/test_full_pipeline.py
import pytest
import asyncio
from app.rag.pipeline import RAGPipeline
from app.memory.short_term import ShortTermMemory
from app.agent.support_agent import support_agent, SupportDependencies

@pytest.mark.asyncio
async def test_full_rag_flow():
    """Test complete RAG pipeline."""
    
    # Initialize components
    rag = RAGPipeline()
    
    # Test query
    query = "What are your business hours?"
    
    # Transform
    transformed = await rag.transform_query(query)
    assert 'rewritten_query' in transformed
    
    # Retrieve
    docs = await rag.retrieve(transformed['rewritten_query'], top_k=20)
    assert len(docs) > 0
    
    # Rerank
    docs_reranked = await rag.rerank(query, docs)
    assert len(docs_reranked) <= 5
    
    print("✓ RAG pipeline test passed")

@pytest.mark.asyncio
async def test_memory_flow():
    """Test memory management."""
    
    redis = ShortTermMemory()
    session_id = "test_session_001"
    
    # Save messages
    await redis.save_message(session_id, "user", "Hello")
    await redis.save_message(session_id, "assistant", "Hi there!")
    
    # Retrieve
    history = await redis.get_history(session_id)
    assert len(history) == 2
    assert history[0]['role'] == 'user'
    
    print("✓ Memory flow test passed")

@pytest.mark.asyncio
async def test_agent_response():
    """Test Pydantic AI agent."""
    
    # Mock dependencies
    deps = SupportDependencies(
        rag_retriever=mock_rag,
        customer_service=mock_customer,
        memory_manager=mock_memory,
        business_context=mock_business
    )
    
    result = await support_agent.run(
        user_message="What are your hours?",
        deps=deps
    )
    
    assert result.output.message is not None
    assert result.output.confidence > 0
    
    print("✓ Agent response test passed")
Phase 9: Deployment & Documentation (Days 31-35)

Day 31-33: Production Docker Compose

# infrastructure/docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_prod:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_prod:/data
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_prod:/qdrant/storage
    restart: unless-stopped

  backend:
    image: smb-support-backend:latest
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ENV=production
    depends_on:
      - postgres
      - redis
      - qdrant
    restart: unless-stopped

  frontend:
    image: smb-support-frontend:latest
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_prod:
  redis_prod:
  qdrant_prod:
Day 34-35: Documentation

# docs/DEPLOYMENT.md

# Deployment Guide - Singapore SMB Support Agent

## Prerequisites

- Docker & Docker Compose
- OpenRouter API key
- Domain name (for production)
- SSL certificates

## Environment Variables

```bash
# .env
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=smb_agent_prod
REDIS_PASSWORD=your_redis_password
OPENROUTER_API_KEY=your_openrouter_key
SECRET_KEY=your_jwt_secret
SITE_URL=https://yourdomain.com
SITE_NAME=Your Business Name
Development Setup

# Clone repository
git clone <repo-url>
cd singapore-smb-support-agent

# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Ingest sample documents
docker-compose exec backend python scripts/ingest_documents.py
Production Deployment

# Use production compose file
docker-compose -f infrastructure/docker-compose.prod.yml up -d

# Access application
# Web: https://yourdomain.com
# API: https://yourdomain.com/api/docs
# WebSocket: wss://yourdomain.com/api/chat/ws/{session_id}
Monitoring

Logs: docker-compose logs -f backend
Health: curl http://localhost:8000/api/health
Metrics: Add Prometheus/ Grafana (optional)

---

## **Phase 10: Validation Checklist**

### **Pre-Implementation Validation**

- [ ] Technology versions confirmed (LangChain 1.0, Pydantic AI 1.39.0)
- [ ] OpenRouter API key obtained
- [ ] WhatsApp Business API account set up (or Twilio)
- [ ] Qdrant requirements reviewed (hardware, storage)
- [ ] Docker environment tested
- [ ] Project structure approved

### **Post-Implementation Validation**

#### **Functionality**
- [ ] User can register/login
- [ ] Web chat accepts messages
- [ ] WhatsApp receives/sends messages
- [ ] Agent retrieves relevant documents from RAG
- [ ] Agent responds with confidence score
- [ ] Sources are displayed for each response
- [ ] Memory persists across messages
- [ ] Escalation triggers on low confidence
- [ ] Support tickets are created

#### **Performance**
- [ ] Response time < 3 seconds (p95)
- [ ] WebSocket connection stable
- [ ] RAG retrieval returns relevant results
- [ ] BGE reranking improves relevance
- [ ] Context compression respects token limits

#### **Quality**
- [ ] Responses are grammatically correct
- [ ] Sources are accurately cited
- [ ] PDPA compliance maintained
- [ ] Singapore context appropriate (SG time, local references)

#### **Deployment**
- [ ] Docker Compose starts all services
- [ ] Database migrations successful
- [ ] Vector store collections created
- [ ] Documents successfully ingested
- [ ] Frontend accessible via browser
- [ ] API docs accessible (/api/docs)

---

## **Summary & Next Steps**

### **What Has Been Designed**

1. ✅ **Complete architecture** validated with latest technologies
2. ✅ **Technology stack** aligned with requirements
3. ✅ **Data flow** optimized for real-time chat
4. ✅ **Memory system** with PDPA-compliant design
5. ✅ **RAG pipeline** with multi-stage retrieval
6. ✅ **MarkItDown integration** for multi-format parsing
7. ✅ **OpenRouter integration** for flexible LLM access
8. ✅ **BGE reranker** for local, cost-effective reranking
9. ✅ **Dual-channel support** (Web + WhatsApp)
10. ✅ **Docker deployment** for dev and production

### **Implementation Timeline**

| Phase | Duration | Key Deliverables |
|--------|------------|------------------|
| 1. Foundation | Days 1-3 | Project structure, databases, Docker setup |
| 2. Ingestion | Days 4-6 | MarkItDown parser, chunking, embeddings, Qdrant |
| 3. RAG Pipeline | Days 7-10 | Query transform, hybrid search, reranking, compression |
| 4. Memory | Days 11-13 | Redis short-term, PG long-term, summarization |
| 5. Agent | Days 14-17 | Pydantic AI agent, tools, system prompts |
| 6. API Layer | Days 18-20 | Chat endpoints, auth, WhatsApp webhook |
| 7. Frontend | Days 21-26 | React UI, Shadcn components, state management |
| 8. Testing | Days 27-30 | Sample data, ingestion, integration tests |
| 9. Deployment | Days 31-35 | Production Docker Compose, documentation |
| **Total** | **35 days** | **Production-ready AI Agent** |

### **Key Risks & Mitigations**

| Risk | Likelihood | Impact | Mitigation |
|-------|------------|---------|-------------|
| MarkItDown parsing errors | Medium | Medium | Fallback to alternative parsers, error handling |
| BGE reranker performance | Low | Medium | Test on local hardware, consider cloud reranker |
| WhatsApp API rate limits | Low | High | Implement queuing, monitor rate limits |
| Token budget overflow | Medium | Medium | Implement strict token counting, aggressive summarization |
| Redis memory limits | Low | Medium | Configure Redis maxmemory, monitor usage |

### **Before You Proceed**

Please confirm:

1. **Environment Variables**: Do you have OpenRouter API key ready?
2. **WhatsApp Setup**: Will you use Meta WhatsApp Business API or Twilio?
3. **Hosting**: Is Docker sufficient, or do you need cloud deployment guides (AWS/GCP/Azure)?
4. **Sample Data**: Should I create the sample documents as described, or will you provide real data?
5. **Timeline**: Is 35 days acceptable, or do you need accelerated/slower pace?

**Once confirmed, I'll begin implementation starting with Phase 1: Foundation Setup.**
