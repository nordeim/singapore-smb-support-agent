# Singapore SMB Customer Support AI Agent - Implementation TODO List

**MVP Scope - English-Only, Core Features, Web Chat**

---

## Phase 1: Foundation Setup (Week 1)

- [x] **1.1** Initialize git repository with .gitignore, README, LICENSE
- [x] **1.2** Create backend/ with pyproject.toml (Python 3.11+, Pydantic AI 1.39+, LangChain 0.3.x)
- [x] **1.3** Initialize frontend/ with package.json (React 18+, TypeScript 5.6+, Tailwind 3.4+)
- [x] **1.4** Initialize Shadcn/UI components (button, input, avatar, scroll-area, dialog)
- [x] **1.5** Create docker-compose.yml with PostgreSQL 16, Redis 7, Qdrant latest, backend, frontend services
- [x] **1.6** Create .env.example with required variables (OPENROUTER_API_KEY, QDRANT_URL, REDIS_URL, DATABASE_URL, SECRET_KEY)

---

## Phase 2: Database Infrastructure (Week 1-2)

- [x] **2.1** Design PostgreSQL schema (users, conversations, messages, conversation_summaries, support_tickets)
- [x] **2.2** Create SQLAlchemy async models with relationships and PDPA compliance fields
- [x] **2.3** Set up Alembic for database migrations
- [x] **2.4** Configure Redis connection with 30min TTL for session storage
- [x] **2.5** Initialize Qdrant client and create collections:
  - `knowledge_base`: 1536-dim (OpenAI embeddings), cosine similarity
  - `conversation_summaries`: Same dimensions for semantic search

---

## Phase 3: Ingestion Pipeline (Week 2)

- [ ] **3.1** Install and integrate MarkItDown library for PDF/DOCX/XLSX/PPTX/HTML/MD/CSV parsing
- [ ] **3.2** Implement semantic chunking with sentence-transformers (target 512± tokens, similarity threshold 0.5)
- [ ] **3.3** Implement recursive character chunking as fallback (separators: `\\n\\n`, `\\n`, `. `, ` `)
- [ ] **3.4** Configure OpenAI embeddings via OpenRouter API
  - Model: `text-embedding-3-small`
  - Base URL: `https://openrouter.ai/api/v1`
- [ ] **3.5** Design metadata schema (source, category, language, created_at, file_name, chunk_index)
- [ ] **3.6** Create ingestion pipeline orchestrator with batch processing capabilities

---

## Phase 4: RAG Pipeline (Week 3)

- [x] **4.1** Create backend/app/rag/pipeline.py orchestrating query_transform → hybrid_retriever → reranker → context_compress
- [x] **4.2** Implement QueryTransformer class with LangChain LLM for:
  - Query rewriting
  - Intent classification
  - Language detection (English-only for MVP)
- [x] **4.3** Implement HybridRetriever using Qdrant native FastEmbedSparse (BM25) + Dense vector search with RRF fusion
- [x] **4.4** Implement BGEReranker using HuggingFaceCrossEncoder
  - Model: `BAAI/bge-reranker-v2-m3` (local model)
  - Top-N selection: 5 documents
- [x] **4.5** Implement ContextCompressor with:
  - Extractive compression
  - Token budget management (~4000 tokens max)
  - Lost-in-middle prevention

---

## Phase 5: Memory System (Week 3-4)

- [x] **5.1** Create backend/app/memory/manager.py orchestrating short_term (Redis) + long_term (PostgreSQL) + summarizer
- [x] **5.2** Implement ShortTermMemory class with:
  - Redis async client
  - Session prefix: `session:{session_id}`
  - 30min TTL
  - Message serialization (JSON)
- [x] **5.3** Implement LongTermMemory class with:
  - SQLAlchemy async session
  - Conversation summaries storage
  - PDPA-compliant data handling (auto-expiry flags)
- [x] **5.4** Implement ConversationSummarizer using:
  - LLM via OpenRouter (GPT-4o-mini for cost-effectiveness)
  - Rolling summary trigger at 20 messages
  - Summary embedding and indexing in Qdrant

---

## Phase 6: Agent Implementation (Week 4-5)

- [x] **6.1** Create backend/app/agent/support_agent.py using Pydantic AI:
  - Model: `'openai/gpt-4o'` (via OpenRouter)
  - Output schema: `SupportResponse` (message, confidence, sources, requires_followup, escalated)
  - Dependencies dataclass: `SupportDependencies` (rag_retriever, customer_service, memory_manager, business_context)
- [x] **6.2** Design system prompt for Singapore SMB customer support:
  - Professional, friendly, culturally aware
  - PDPA compliance guidelines
  - English-primary language
  - Escalation thresholds
- [x] **6.3** Create `@support_agent.tool retrieve_knowledge(query: str) → str` executing full RAG pipeline
- [x] **6.4** Create `@support_agent.tool get_customer_info(customer_id: str) → str` for database lookup
- [x] **6.5** Create `@support_agent.tool check_business_hours() → str` with Singapore timezone (Asia/Singapore) logic
- [x] **6.6** Create `@support_agent.tool escalate_to_human(reason: str, conversation_id: str) → str` for human handoff with ticket creation
- [x] **6.7** Implement response validators:
  - Confidence threshold (< 0.7 triggers escalation)
  - Sentiment analysis (negative → escalate)
  - PDPA compliance check

---

## Phase 7: API Layer (Week 5-6)

- [x] **7.1** Create backend/app/api/routes/chat.py with:
  - POST `/api/chat` endpoint
  - WebSocket support for real-time streaming
  - Request/response schemas (`ChatRequest`, `ChatResponse`)
- [x] **7.2** Create backend/app/api/routes/auth.py with:
  - POST `/api/auth/register` endpoint
  - POST `/api/auth/login` endpoint
  - JWT token generation using `python-jose`
- [x] **7.3** Create backend/app/dependencies.py with:
  - `get_current_user(token: str)` function
  - `get_memory_manager()` function
  - `get_db()` function
  - `get_business_context()` function
- [x] **7.4** Create backend/app/config.py using pydantic-settings for:
  - Environment variable management
  - OpenRouter base_url configuration
  - Secret key management
- [x] **7.5** Create backend/app/models/schemas.py (API Pydantic models)
- [x] **7.6** Create backend/app/models/domain.py (domain models)
- [x] **7.7** Create backend/app/models/database.py (SQLAlchemy models)
- [x] **7.8** Create backend/app/main.py FastAPI app with:
  - CORS configuration
  - WebSocket integration
  - Middleware (logging, error handling)
  - Lifecycle events (startup, shutdown)

---

## Phase 8: Frontend Development (Week 6-7)

- [ ] **8.1** Install Shadcn/UI CLI, add components:
  - button
  - input
  - avatar
  - scroll-area
  - dialog
- [ ] **8.2** Create frontend/src/components/chat/ChatWidget.tsx (main container with):
  - Header with status and business hours
  - Messages scroll area
  - Input field with send button
  - Typing indicator
- [ ] **8.3** Create frontend/src/components/chat/ChatHeader.tsx with:
  - Status indicator (online/offline)
  - Business hours display
  - Agent name
- [ ] **8.4** Create frontend/src/components/chat/ChatMessages.tsx scrollable message list with:
  - ScrollArea from Shadcn/UI
  - Auto-scroll to bottom on new message
- [ ] **8.5** Create frontend/src/components/chat/ChatMessage.tsx with:
  - User bubble (right-aligned)
  - Assistant bubble (left-aligned)
  - Timestamp
  - Source citations display
- [ ] **8.6** Create frontend/src/components/chat/ChatInput.tsx with:
  - Textarea (auto-expand)
  - Send button
  - Character count
  - Enter key submit handling
- [ ] **8.7** Create frontend/src/components/chat/TypingIndicator.tsx animated component with:
  - 3-dot loading animation
  - Fade in/out transitions
- [ ] **8.8** Create frontend/src/lib/api.ts fetch wrapper with:
  - Fetch interceptor
  - Error handling
  - Request/response types
- [ ] **8.9** Create frontend/src/lib/websocket.ts WebSocket client with:
  - Reconnection logic
  - Heartbeat/ping-pong (30s interval)
  - Message streaming
- [ ] **8.10** Create frontend/src/stores/chatStore.ts Zustand store with:
  - Messages array
  - Session ID
  - Connection status
  - isTyping flag
- [ ] **8.11** Create frontend/src/types/index.ts with:
  - Message type
  - ChatRequest type
  - ChatResponse type
  - Source type
  - User type
  - Session type

---

## Phase 9: Data Preparation & Ingestion (Week 7)

- [ ] **9.1** Create sample FAQs in Singapore SMB context:
  - Pricing (service tiers, discounts)
  - Business hours (operating schedule)
  - Services (offerings, features)
  - Returns/Refunds (policies, process)
  - Shipping (delivery options, tracking)
- [ ] **9.2** Create sample products catalog with:
  - Product names and descriptions
  - Pricing and availability
  - Technical specifications
- [ ] **9.3** Create sample policies:
  - Terms of service
  - Privacy policy (PDPA-compliant)
  - Return policy
  - Shipping policy
- [ ] **9.4** Create backend/scripts/ingest_documents.py CLI tool with:
  - MarkItDown parsing (PDF/DOCX/XLSX/PPTX/HTML/MD/CSV)
  - Semantic chunking
  - OpenAI embeddings via OpenRouter
  - Qdrant upsert operations
  - Batch processing support
- [ ] **9.5** Test ingestion pipeline with sample documents
- [ ] **9.6** Verify Qdrant collection population and metadata

---

## Phase 10: Testing & Dockerization (Week 8)

- [ ] **10.1** Create backend/tests/unit/test_rag.py for:
  - RAG pipeline testing
  - Query transformation
  - Hybrid retrieval
  - Reranking
- [ ] **10.2** Create backend/tests/unit/test_memory.py for:
  - Memory manager
  - Short-term memory (Redis)
  - Long-term memory (PostgreSQL)
  - Conversation summarizer
- [ ] **10.3** Create backend/tests/unit/test_agent.py for:
  - Agent tool testing
  - Response validation
  - Escalation logic
- [ ] **10.4** Create backend/tests/integration/test_api.py for:
  - API endpoint testing
  - Authentication flow
  - Error handling
- [ ] **10.5** Create backend/tests/integration/test_pipeline.py for:
  - End-to-end chat flow
  - Mocked dependencies
  - Full system integration
- [ ] **10.6** Create backend/Dockerfile with:
  - Multi-stage build
  - Healthcheck
  - Non-root user
  - Python 3.11-slim base
- [ ] **10.7** Create frontend/Dockerfile with:
  - Nginx reverse proxy
  - Build optimization
  - Production-ready image
  - Node 20-alpine builder
- [ ] **10.8** Create infrastructure/docker-compose.yml with:
  - PostgreSQL 16 service
  - Redis 7 service
  - Qdrant latest service
  - Backend service
  - Frontend service
  - Volume mounts for persistence
  - Environment variable configuration
- [ ] **10.9** Test Docker build and deployment locally

---

## Phase 11: Documentation (Week 8)

- [ ] **11.1** Create comprehensive README.md with:
  - Project overview
  - Quick start guide
  - Technology stack
  - Development setup instructions
- [ ] **11.2** Create docs/ARCHITECTURE.md with:
  - System architecture diagrams
  - Component interactions
  - Data flow diagrams
- [ ] **11.3** Create docs/API.md with:
  - Endpoint documentation
  - Request/response examples
  - Authentication details
- [ ] **11.4** Create docs/DEPLOYMENT.md with:
  - Deployment instructions
  - Environment variable guide
  - Troubleshooting section
- [ ] **11.5** Create docs/TROUBLESHOOTING.md with:
  - Common issues and solutions
  - Debugging guide
  - FAQ

---

## Success Criteria Checklist

### Functional Requirements
- [ ] Agent handles customer enquiries in English
- [ ] Responses grounded in knowledge base (RAG)
- [ ] Conversation context maintained across messages
- [ ] Escalation when confidence < 0.7 or negative sentiment
- [ ] PDPA-compliant data handling with consent tracking
- [ ] Response latency < 3 seconds (p95)

### RAG Quality Metrics (RAGAS Evaluation)
- [ ] Faithfulness > 0.90 (minimum > 0.85)
- [ ] Answer Relevancy > 0.85 (minimum > 0.80)
- [ ] Context Precision > 0.80 (minimum > 0.75)
- [ ] Context Recall > 0.85 (minimum > 0.80)

### Performance Requirements
- [ ] Response Time (p50) < 1.5s
- [ ] Response Time (p95) < 3.0s
- [ ] Concurrent Users: 100+
- [ ] Uptime: 99.5%
- [ ] Error Rate: < 0.1%

### Frontend Requirements
- [ ] Accessible (WCAG AA compliance)
- [ ] Mobile responsive (320px - 2560px)
- [ ] Real-time message streaming
- [ ] Graceful error handling

---

## Notes

- **MVP Scope**: English-only, core features, web chat
- **Cost Optimization**: OpenRouter API with GPT-4o-mini for most queries
- **PDPA Compliance**: 30-day default TTL, consent tracking, data minimization
- **Deployment**: Local Docker Compose for development and testing
- **Future Enhancements**: Multilingual support, WhatsApp integration, advanced analytics

---

**Total Tasks: 68 (45 implementation + 23 success criteria)**
**Estimated Timeline: 8 weeks**
