# Singapore SMB Customer Enquiry Support AI Agent - Implementation Plan

**Optimized for Singapore Small-to-Medium Businesses (MVP)**

---

## Executive Summary

This implementation plan has been **meticulously refined** based on optimal technical choices for Singapore SMBs. The plan delivers a production-ready AI customer support agent with advanced RAG capabilities, hierarchical memory management, and PDPA compliance in a focused MVP scope.

**User-Selected Technical Approach:**
- ✅ **OpenRouter API** (Cost-effective, 100+ models, fallback capability)
- ✅ **Qdrant Native Sparse Search** (FastEmbedSparse with BM25)
- ✅ **MVP Scope** (English-only, core features, web chat)
- ✅ **Real Business Data** (Pipeline ready for your documents)
- ✅ **Local Docker Compose** Deployment
- ✅ **Professional Shadcn/UI** Styling

---

## Phase 1: Foundation Setup (Week 1)

### 1.1 Project Structure

```
singapore-smb-support-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry
│   │   ├── config.py                  # Configuration management
│   │   ├── dependencies.py            # Dependency injection
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py            # Chat endpoints
│   │   │   │   └── auth.py            # Authentication endpoints
│   │   │   └── websocket.py           # WebSocket handlers
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── support_agent.py       # Pydantic AI agent definition
│   │   │   ├── tools/
│   │   │   ├── prompts/
│   │   │   └── validators.py
│   │   ├── rag/
│   │   │   ├── pipeline.py
│   │   │   ├── retriever.py
│   │   │   ├── reranker.py
│   │   │   ├── query_transform.py
│   │   │   └── context_compress.py
│   │   ├── ingestion/
│   │   │   ├── pipeline.py
│   │   │   ├── parsers/
│   │   │   ├── chunkers/
│   │   │   └── embedders/
│   │   ├── memory/
│   │   │   ├── manager.py
│   │   │   ├── short_term.py
│   │   │   ├── long_term.py
│   │   │   └── summarizer.py
│   │   └── models/
│   │       ├── schemas.py
│   │       ├── domain.py
│   │       └── database.py
│   ├── tests/
│   ├── scripts/
│   ├── data/
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   └── chat/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── stores/
│   │   └── types/
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile
├── infrastructure/
│   └── docker-compose.yml
└── docs/
```

### 1.2 Phase 1 Tasks

- [ ] Initialize git repository with .gitignore, README, LICENSE
- [ ] Create backend/ with pyproject.toml (Python 3.11+, Pydantic AI 1.39+, LangChain 0.3.x)
- [ ] Initialize frontend/ with package.json (React 18+, TypeScript 5.6+, Tailwind 3.4+)
- [ ] Initialize Shadcn/UI components (button, input, avatar, scroll-area, dialog)
- [ ] Create docker-compose.yml with PostgreSQL 16, Redis 7, Qdrant latest, backend, frontend services
- [ ] Create .env.example with required variables

---

## Phase 2: Database Infrastructure (Week 1-2)

### 2.1 PostgreSQL Schema Design

**Tables:**

| Table | Purpose | Key Fields |
|-------|---------|-------------|
| `users` | User authentication | id, email, hashed_password, created_at |
| `conversations` | Conversation tracking | id, user_id, session_id, started_at, ended_at |
| `messages` | Individual messages | id, conversation_id, role (user/assistant), content, created_at |
| `conversation_summaries` | Rolling summaries | id, conversation_id, summary, created_at, metadata |
| `support_tickets` | Escalated tickets | id, conversation_id, reason, status, created_at, assigned_to |

### 2.2 Phase 2 Tasks

- [ ] Design PostgreSQL schema with PDPA compliance fields (created_at, auto_expiry)
- [ ] Create SQLAlchemy async models with relationships
- [ ] Set up Alembic for database migrations
- [ ] Configure Redis connection with 30min TTL for session storage
- [ ] Initialize Qdrant client and create collections:
  - `knowledge_base`: 1536-dim (OpenAI embeddings), cosine similarity
  - `conversation_summaries`: Same dimensions for semantic search

---

## Phase 3: Ingestion Pipeline (Week 2)

### 3.1 Document Parsing with MarkItDown

**Supported Formats:**
- PDF, DOCX, XLSX, PPTX, HTML, Markdown, CSV

**Process:**
1. MarkItDown parses document to clean text
2. Metadata extraction (filename, page_count, document_type)
3. Language detection (English-only for MVP)

### 3.2 Chunking Strategy

**Primary: Semantic Chunking**
- Target: 512± tokens
- Method: Sentence-level embedding similarity
- Split threshold: 0.5 cosine similarity
- Model: sentence-transformers/all-MiniLM-L6-v2

**Fallback: Recursive Character Chunking**
- Separators: `["\n\n", "\n", ". ", " "]`
- Chunk size: 500 characters
- Overlap: 100 characters

### 3.3 Metadata Schema

```python
{
  "source": "faq|product|policy|website",
  "category": "pricing|hours|services|returns|shipping",
  "language": "en",
  "created_at": "ISO8601 timestamp",
  "file_name": "original_filename.ext",
  "chunk_index": 0
}
```

### 3.4 Phase 3 Tasks

- [ ] Install and integrate MarkItDown library
- [ ] Implement semantic chunking with sentence-transformers
- [ ] Implement recursive character chunking as fallback
- [ ] Configure OpenAI embeddings via OpenRouter API
  - Model: `text-embedding-3-small`
  - Base URL: `https://openrouter.ai/api/v1`
- [ ] Design metadata schema with above fields
- [ ] Create ingestion pipeline with batch processing

---

## Phase 4: RAG Pipeline (Week 3)

### 4.1 Multi-Stage Pipeline Architecture

```
Query → Query Transformation → Hybrid Retrieval → Reranking → Context Compression → Response Generation
```

### 4.2 Query Transformation

- Query rewriting with LLM (LangChain)
- Intent classification (informational, transactional, conversational)
- Language detection (English-only for MVP, prepared for future expansion)

### 4.3 Hybrid Retrieval (Qdrant Native)

**Components:**
1. **Dense Vector Search**: Qdrant semantic similarity
2. **Sparse Search (BM25)**: Qdrant FastEmbedSparse
3. **Fusion**: Reciprocal Rank Fusion (RRF)

**Implementation:**
```python
from langchain_qdrant import FastEmbedSparse, RetrievalMode

sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
qdrant = QdrantVectorStore.from_documents(
    docs,
    embedding=embeddings,
    sparse_embedding=sparse_embeddings,
    retrieval_mode=RetrievalMode.HYBRID,
)
```

### 4.4 Reranking

**Model:** BAAI/bge-reranker-v2-m3 (Local HuggingFace model)
- Method: Cross-encoder
- Top-N selection: 5 documents
- Purpose: Refine relevance before generation

**Implementation:**
```python
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
compressor = CrossEncoderReranker(model=model, top_n=5)
```

### 4.5 Context Compression

**Budget:** ~4000 tokens max for working memory

**Methods:**
1. Extractive: Keep only relevant sentences
2. Token budget management: Prune least relevant
3. Lost-in-middle prevention: Place key info at start/end

### 4.6 Phase 4 Tasks

- [ ] Create RAG pipeline orchestrator
- [ ] Implement QueryTransformer class
- [ ] Implement HybridRetriever with Qdrant FastEmbedSparse
- [ ] Implement BGE Reranker using HuggingFaceCrossEncoder
- [ ] Implement ContextCompressor with token budgeting

---

## Phase 5: Memory System (Week 3-4)

### 5.1 Hierarchical Memory Architecture

```
┌─────────────────────────────────────────┐
│       WORKING MEMORY             │
│    (Immediate LLM Context)      │
│    - System prompt               │
│    - Retrieved chunks             │
│    - Compressed conversation       │
│    - Current query                │
│    Token Budget: ~4000 tokens     │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│       SHORT-TERM MEMORY          │
│    (Session/Conversation)        │
│    Storage: Redis                 │
│    TTL: 30 minutes               │
│    - Full conversation history      │
│    - Session metadata             │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│       LONG-TERM MEMORY           │
│    (Persistent Knowledge)         │
│    Storage: PostgreSQL            │
│    Retention: PDPA-compliant      │
│    - Conversation summaries       │
│    - Historical interactions      │
│    - Customer profiles            │
└─────────────────────────────────┘
```

### 5.2 Short-Term Memory (Redis)

**Configuration:**
- Session prefix: `session:{session_id}`
- TTL: 30 minutes (configurable)
- Storage: JSON serialized messages

**Key Methods:**
- `get_session(session_id)`: Retrieve full conversation
- `add_message(session_id, message)`: Append to session
- `delete_session(session_id)`: Clear on session end

### 5.3 Long-Term Memory (PostgreSQL)

**Tables:**
- `conversations`: Metadata, timestamps
- `messages`: Individual message history
- `conversation_summaries`: LLM-generated summaries

**PDPA Compliance:**
- Auto-expiry flags (30 days default)
- Data minimization (store only essential)
- Consent tracking (separate table)

### 5.4 Summarization

**Trigger:** 20 messages in session

**Process:**
1. LLM summarizes last 15 messages
2. Summary stored in `conversation_summaries`
3. Summary embedded and indexed in Qdrant
4. Messages archived but retained for audit trail

**Model:** OpenRouter GPT-4o-mini for cost-effective summarization

### 5.5 Phase 5 Tasks

- [ ] Create MemoryManager orchestrator
- [ ] Implement ShortTermMemory (Redis async client)
- [ ] Implement LongTermMemory (SQLAlchemy async)
- [ ] Implement ConversationSummarizer with rolling trigger

---

## Phase 6: Agent Implementation (Week 4-5)

### 6.1 Pydantic AI Agent Design

```python
from pydantic_ai import Agent, RunContext

class SupportDependencies:
    rag_retriever: RAGRetriever
    customer_service: CustomerService
    memory_manager: MemoryManager
    business_context: BusinessContext

support_agent = Agent(
    model='openai/gpt-4o',
    deps_type=SupportDependencies,
    output_type=SupportResponse,
    instructions="You are a Singapore SMB customer support specialist..."
)
```

### 6.2 System Prompt

```
You are a professional, friendly customer support specialist for Singapore Small-to-Medium Businesses.

Your Role:
- Help customers with product/service enquiries
- Provide accurate information based on knowledge base
- Escalate complex issues to human agents when needed

Guidelines:
- Language: English (primary), respond clearly and professionally
- Tone: Friendly, helpful, culturally aware (Singapore context)
- PDPA Compliance: Never share personal information without consent
- Business Hours: Check current operating hours before making commitments
- Confidence: If unsure or confidence < 0.7, escalate to human

Available Tools:
- retrieve_knowledge(query): Search knowledge base
- get_customer_info(customer_id): Look up customer details
- check_business_hours(): Check current operating status
- escalate_to_human(reason, context): Handoff to human agent

Remember: Ground all responses in retrieved knowledge. Do not hallucinate information.
```

### 6.3 Tool Definitions

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `retrieve_knowledge` | RAG search | `query: str` | `str` (relevant context) |
| `get_customer_info` | Customer lookup | `customer_id: str` | `str` (customer profile) |
| `check_business_hours` | Operating hours | None | `str` (hours status) |
| `escalate_to_human` | Human handoff | `reason: str, conversation_id: str` | `str` (ticket confirmation) |

### 6.4 Response Validation

**Validators:**
1. Confidence threshold (< 0.7 → escalate)
2. Sentiment analysis (negative → escalate)
3. PDPA compliance check
4. Source citation requirement

**Schema:**
```python
class SupportResponse(BaseModel):
    message: str
    confidence: float
    sources: List[SourceCitation]
    requires_followup: bool
    escalated: bool
    ticket_id: Optional[str]
```

### 6.5 Phase 6 Tasks

- [ ] Create Pydantic AI agent with SupportDependencies
- [ ] Design system prompt for Singapore SMB context
- [ ] Implement retrieve_knowledge tool (RAG pipeline)
- [ ] Implement get_customer_info tool (DB lookup)
- [ ] Implement check_business_hours tool (SG timezone)
- [ ] Implement escalate_to_human tool (ticket creation)
- [ ] Implement response validators

---

## Phase 7: API Layer (Week 5-6)

### 7.1 REST Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | User login (JWT) |
| `/api/chat` | POST | Send message, get response |
| `/api/chat/history/{session_id}` | GET | Retrieve conversation history |
| `/api/feedback` | POST | Submit feedback |

### 7.2 WebSocket

**Endpoint:** `/ws/chat/{session_id}`

**Features:**
- Real-time message streaming
- Heartbeat/ping-pong (30s interval)
- Automatic reconnection
- Connection status updates

### 7.3 Dependency Injection

```python
async def get_current_user(token: str = Depends(verify_jwt)):
    return await get_user_by_token(token)

async def get_memory_manager():
    return MemoryManager(redis, db)

async def get_business_context():
    return BusinessContext(timezone="Asia/Singapore")
```

### 7.4 Phase 7 Tasks

- [ ] Create chat.py (POST /api/chat, WebSocket)
- [ ] Create auth.py (register, login, JWT)
- [ ] Create dependencies.py (DI functions)
- [ ] Create config.py (Pydantic Settings)
- [ ] Create schemas.py (API models)
- [ ] Create domain.py (domain models)
- [ ] Create database.py (SQLAlchemy models)
- [ ] Create main.py (FastAPI app with CORS, middleware)

---

## Phase 8: Frontend Development (Week 6-7)

### 8.1 Technology Stack

- React 18+
- TypeScript 5.6+
- Tailwind CSS 3.4+
- Shadcn/UI components
- Zustand (state management)
- TanStack React Query (server state)

### 8.2 Component Architecture

```
ChatWidget (container)
├── ChatHeader
│   ├── Status indicator
│   ├── Business hours
│   └── Agent name
├── ChatMessages (scroll area)
│   └── ChatMessage[]
│       ├── User bubble
│       ├── Assistant bubble
│       └── Source citations
├── ChatInput
│   ├── Textarea
│   ├── Send button
│   └── Character count
└── TypingIndicator
```

### 8.3 Phase 8 Tasks

- [ ] Install Shadcn/UI CLI, add components
- [ ] Create ChatWidget.tsx (main container)
- [ ] Create ChatHeader.tsx (status, hours, agent name)
- [ ] Create ChatMessages.tsx (scrollable list)
- [ ] Create ChatMessage.tsx (bubbles, timestamps, citations)
- [ ] Create ChatInput.tsx (textarea, send button)
- [ ] Create TypingIndicator.tsx (animated dots)
- [ ] Create api.ts (fetch wrapper)
- [ ] Create websocket.ts (WebSocket client)
- [ ] Create chatStore.ts (Zustand store)
- [ ] Create types/index.ts (TypeScript types)

---

## Phase 9: Data Preparation & Ingestion (Week 7)

### 9.1 Sample Data Categories

**FAQs:**
- Pricing (service tiers, discounts)
- Business hours (operating schedule)
- Services (offerings, features)
- Returns/Refunds (policies, process)
- Shipping (delivery options, tracking)

**Products:**
- Product catalog with descriptions
- Pricing and availability
- Technical specifications

**Policies:**
- Terms of service
- Privacy policy (PDPA-compliant)
- Return policy
- Shipping policy

### 9.2 Ingestion Script

**CLI Tool:** `backend/scripts/ingest_documents.py`

**Usage:**
```bash
python scripts/ingest_documents.py \
  --input_dir ./data/documents \
  --collection knowledge_base \
  --chunking semantic \
  --batch_size 100
```

### 9.3 Phase 9 Tasks

- [ ] Create sample FAQs (Singapore SMB context)
- [ ] Create sample products catalog
- [ ] Create sample policies (PDPA-compliant)
- [ ] Create ingestion CLI script
- [ ] Test ingestion with MarkItDown parsing
- [ ] Test semantic chunking and embeddings

---

## Phase 10: Testing & Dockerization (Week 8)

### 10.1 Unit Tests

**Test Files:**
- `backend/tests/unit/test_rag.py` (RAG pipeline)
- `backend/tests/unit/test_memory.py` (memory manager)
- `backend/tests/unit/test_agent.py` (agent tools)

**Framework:** pytest-asyncio, pytest-mock

### 10.2 Integration Tests

**Test Files:**
- `backend/tests/integration/test_api.py` (API endpoints)
- `backend/tests/integration/test_pipeline.py` (E2E chat flow)

**Coverage:** Critical paths only (MVP scope)

### 10.3 Docker Configuration

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

**Docker Compose:**
```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: support_agent
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  backend:
    build: ./backend
    depends_on:
      - postgres
      - redis
      - qdrant
    environment:
      DATABASE_URL: postgresql://...
      REDIS_URL: redis://redis:6379
      QDRANT_URL: http://qdrant:6333
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### 10.4 Phase 10 Tasks

- [ ] Create unit tests for RAG, memory, agent
- [ ] Create integration tests for API, pipeline
- [ ] Create backend Dockerfile (multi-stage)
- [ ] Create frontend Dockerfile (Nginx)
- [ ] Create docker-compose.yml with all services
- [ ] Test Docker build and deployment

---

## Phase 11: Documentation (Week 8)

### 11.1 README Structure

```markdown
# Singapore SMB Customer Support AI Agent

## Quick Start
1. Clone repository
2. Copy .env.example to .env
3. Fill in required environment variables
4. Run `docker-compose up -d`
5. Access frontend at http://localhost:3000

## Architecture
[System diagram and component overview]

## API Documentation
[Endpoint descriptions with examples]

## Data Ingestion
[Instructions for uploading documents]

## Troubleshooting
[Common issues and solutions]
```

### 11.2 Phase 11 Tasks

- [ ] Create comprehensive README.md
- [ ] Create ARCHITECTURE.md with diagrams
- [ ] Create API.md with endpoint documentation
- [ ] Create DEPLOYMENT.md with deployment instructions
- [ ] Create TROUBLESHOOTING.md

---

## Success Criteria

### Functional Requirements

- ✅ Agent handles customer enquiries in English
- ✅ Responses grounded in knowledge base (RAG)
- ✅ Conversation context maintained across messages
- ✅ Escalation when confidence < 0.7 or negative sentiment
- ✅ PDPA-compliant data handling
- ✅ Response latency < 3 seconds (p95)

### RAG Quality Metrics (RAGAS Evaluation)

| Metric | Target | Minimum |
|--------|--------|----------|
| Faithfulness | > 0.90 | > 0.85 |
| Answer Relevancy | > 0.85 | > 0.80 |
| Context Precision | > 0.80 | > 0.75 |
| Context Recall | > 0.85 | > 0.80 |

### Performance Requirements

| Metric | Target |
|--------|--------|
| Response Time (p50) | < 1.5s |
| Response Time (p95) | < 3.0s |
| Concurrent Users | 100+ |
| Uptime | 99.5% |
| Error Rate | < 0.1% |

---

## Risk Mitigation Strategies

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-------------|
| LLM Hallucination | Medium | High | Strict retrieval grounding, confidence scoring, source citation |
| PDPA Violation | Low | Critical | Data minimization, consent tracking, auto-expiry |
| Context Overflow | Medium | Medium | Rolling summarization, token budget management |
| Poor Retrieval | Medium | High | Hybrid search, cross-encoder reranking, RAGAS evaluation |
| Latency Issues | Medium | Medium | Async processing, streaming responses, caching |
| Cost Overrun | Low | Medium | GPT-4o-mini primary, token monitoring, rate limiting |

---

## Deployment

### Local Development

```bash
docker-compose up -d
```

### Production (Future)

- Cloud provider selection (AWS/GCP/Azure/DigitalOcean)
- SSL/TLS configuration
- Domain setup
- Monitoring and alerting
- Backup and disaster recovery

---

## Next Steps After MVP

1. **Multilingual Support**: Add Mandarin Chinese capabilities
2. **WhatsApp Integration**: Multi-channel support
3. **Advanced Analytics**: Usage metrics and insights
4. **Knowledge Management UI**: Admin interface for documents
5. **Performance Optimization**: Query caching, connection pooling

---

**This implementation plan is ready for execution. All technical choices validated, architecture designed, and tasks defined.**
