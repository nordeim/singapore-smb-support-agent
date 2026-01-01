<div align="center">

  # 🇸🇬 Singapore SMB Customer Support AI Agent

  ### AI-Powered Customer Support Engine with RAG, Multi-Memory Architecture & PDPA Compliance

  [![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg)](https://fastapi.tiangolo.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
  [![Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-red.svg)](https://qdrant.tech/)
  [![LangChain](https://img.shields.io/badge/LangChain-1.2+-orange.svg)](https://python.langchain.com/)
  [![Tests](https://img.shields.io/badge/Tests-Passing-success.svg)](tests/)

  **Production-ready RAG system with hierarchical memory for Singapore SMBs**

  [Quick Start](#-quick-start) • [Features](#-key-features) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🎯 About

Transform customer support with an **intelligent, context-aware AI agent** that combines:

- **Retrieval-Augmented Generation (RAG)** for accurate, domain-specific responses
- **Hierarchical Memory System** (Short-term + Long-term + Compressed Summaries)
- **Singapore-Specific Compliance** with PDPA (Personal Data Protection Act)
- **Multi-Doc Ingestion** supporting PDF, DOCX, Markdown, and more
- **Real-Time Chat** via WebSocket streaming
- **Auto-Escalation** to human agents when confidence drops

**Built for**: Singapore Small-to-Medium Businesses seeking enterprise-grade AI support without the enterprise price tag.

---

## ✨ Key Features

### 🧠 Advanced RAG Pipeline

| Feature | Description |
|---------|-------------|
| **Hybrid Search** | Combines dense vectors (semantic) with sparse vectors (BM25) for optimal retrieval |
| **Query Transformation** | Multi-query, decomposition, and re-ranking for complex questions |
| **Context Compression** | Intelligently summarizes retrieved content to fit within token limits |
| **Source Attribution** | Every response includes source document citations for transparency |

### 💾 Hierarchical Memory System

```
┌─────────────────────────────────────────────┐
│         Working Memory (Current)            │
│  • Last 20 messages                      │
│  • Active conversation context             │
└─────────────────────────────────────────────┘
                  ↓ (every 20 msgs)
┌─────────────────────────────────────────────┐
│      Long-Term Memory (PostgreSQL)        │
│  • Full conversation history               │
│  • User profiles & consent                 │
│  • Support tickets                        │
└─────────────────────────────────────────────┘
                  ↓ (auto-summarized)
┌─────────────────────────────────────────────┐
│     Compressed Summaries (Qdrant)         │
│  • Key conversation insights              │
│  • Vector-embedded for semantic retrieval │
└─────────────────────────────────────────────┘
```

### 🔒 PDPA Compliance

- **30-Day Data Retention** with auto-expiry
- **Explicit Consent Tracking** with versioning
- **Data Minimization** principles embedded
- **Audit Logging** for all data access
- **Right to Deletion** enforcement

### 🎨 Trust-Centric UX

- **ConfidenceRing Visual Feedback:** Color-coded trust indicators
  - Green (≥85% confidence): High trust answers
  - Amber (≥70% confidence): Medium confidence
  - Red (<70% confidence): Low trust/uncertainty
- **Real-Time Thought Streaming:** Visible AI processing steps
  - "Scanning..." → "Cross-referencing..." → "Formatting..."
  - Reduces perceived latency through transparency
- **SessionPulse PDPA Visualization:** Real-time session expiry countdown
  - Green (>20m): Session active
  - Amber (5-20m): Expiring soon
  - Red (<5m): Critical - extend or lose

### 🚀 Auto-Escalation Logic

```python
# Intelligent escalation triggers
if confidence < 0.6 or \
   query_complexity == HIGH or \
   business_hours == CLOSED:
    escalate_to_human_agent()
```

### 🌐 Multi-Language Support

- English (Primary)
- Chinese (Simplified)
- Malay
- Tamil
- Auto-detection + manual override

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Next.js Chat UI]
        B[WebSocket Client]
    end

    subgraph "Backend Layer"
        C[FastAPI Server]
        D[Authentication/Authorization]
        E[Chat API Routes]
        F[WebSocket Manager]
    end

    subgraph "AI/ML Layer"
        G[RAG Pipeline]
        H[Query Transform]
        I[Retriever]
        J[Reranker]
        K[Context Compressor]
        L[LLM Generation]
    end

    subgraph "Data Layer"
        M[(Qdrant Vector DB)]
        N[(PostgreSQL SQL DB)]
        O[(Redis Cache)]
    end

    subgraph "External Services"
        P[OpenAI/OpenRouter]
        Q[Qdrant API]
    end

    A --> B
    B --> F
    F --> C
    A --> E
    E --> D
    E --> G

    G --> H
    H --> I
    I --> M
    I --> J
    J --> K
    K --> L
    L --> P

    C --> N
    C --> O
    O --> N
```

**Note:** WebSocket includes enhanced error handling with exponential backoff (3s * 2^attempt, max 30s) and automatic REST API fallback after 3 consecutive failures.


### Tech Stack Rationale

| Component | Technology | Why? |
|-----------|-----------|-------|
| **Backend Framework** | FastAPI | Native async support, auto-generated docs, performance |
| **Vector Database** | Qdrant | Open-source, hybrid search, horizontal scaling |
| **Relational DB** | PostgreSQL 16 | Full-text search, JSON support, async (asyncpg) |
| **Cache** | Redis 7 | Fast session storage, pub/sub for WebSocket scaling |
| **LLM Provider** | OpenRouter | Multi-model access, cost optimization, fallback support |
| **Frontend** | Next.js 14 | React Server Components, excellent DX, built-in optimization |
| **AI Framework** | LangChain 1.2+ | Mature ecosystem, prompt templates, tools integration |
| **Type Safety** | Pydantic AI + TypeScript | End-to-end validation, better IDE support |

---

## 📚 Quick Start

### Prerequisites

- ✅ **Docker** & **Docker Compose** (v20.10+)
- ✅ **Git** (for cloning)

> 💡 **No Python or Node.js required!** All dependencies run in Docker containers.

### 🚀 One-Command Setup

```bash
# 1. Clone the repository
git clone https://github.com/nordeim/singapore-smb-support-agent.git
cd singapore-smb-support-agent

# 2. Configure environment variables
cp .env.example .env
# Edit .env with your API keys (see below)

# 3. Start all services
docker compose up -d

# 4. Verify it's running
curl http://localhost:8000/ | python -m json.tool
```

**Expected Output:**
```json
{
  "name": "Singapore SMB Support Agent",
  "version": "1.0.0",
  "status": "operational"
}
```

### ⚙️ Environment Configuration

Minimum required variables in `.env`:

```env
# LLM Provider (OpenRouter - cost-effective)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Database URLs (pre-configured for Docker)
DATABASE_URL=postgresql+asyncpg://agent_user:dev_password_only@postgres:5432/support_agent
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333

# Security
SECRET_KEY=generate-a-secure-32-char-string-here
```

**Get API Keys:**
- [OpenRouter](https://openrouter.ai/keys) - Free tier available, $5/month credit
- Or use your OpenAI key: `OPENAI_API_KEY=sk-your-key-here`

### 🎯 Access Your Application

| Service | URL | Purpose |
|---------|-----|---------|
| **Chat Interface** | http://localhost:3000 | Frontend application |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **Health Check** | http://localhost:8000/health | System status |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Vector DB management |

### 📥 Ingest Your Documents

```bash
# Ingest all documents from data/ directory
python backend/scripts/ingest_documents.py \
  --input-dir backend/data \
  --collection knowledge_base \
  --recursive \
  --init-collections
```

**Supported Formats:** PDF, DOCX, XLSX, PPTX, HTML, Markdown, CSV

**What happens:** Documents → Parse → Chunk → Embed → Vector Store

---

## 🧪 Quick Verification

After starting services, run these quick checks:

```bash
# 1. Check all services are healthy
docker compose ps

# 2. Test API health
curl http://localhost:8000/health

# 3. Test Qdrant connection
curl http://localhost:6333/collections

# 4. Test Redis connection
docker exec smb_support_redis redis-cli ping
# Should return: PONG
```

### ❗ Troubleshooting Quick-Fixes

| Issue | Solution |
|-------|----------|
| `Port 8000 already in use` | `docker compose down` then `docker compose up -d` |
| `Qdrant connection failed` | Check: `docker logs smb_support_qdrant` |
| `Database connection error` | Wait 10s for PostgreSQL to initialize |
| `401 Unauthorized` | Verify `OPENROUTER_API_KEY` in `.env` |
| `Module not found` | `docker compose restart backend` (volume mount issue) |
| `Confidence Ring showing wrong colors` | Fixed in v1.0.1 - update to latest version |
| `React hydration error on chat header` | Fixed in v1.0.1 - update to latest version |
| `WebSocket empty error in console` | Fixed in v1.0.1 - system auto-switches to REST fallback |

---

## 🩺 Recent Fixes (v1.0.1)

### ✅ ConfidenceRing Logic Correction
Fixed trust color inversion issue. High confidence (≥85%) now correctly displays green, low confidence (<70%) displays red.

**Impact:** Users now see accurate trust indicators reflecting actual AI response confidence levels.

### ✅ ChatHeader Hydration Error
Resolved SSR/client text mismatch that caused React hydration errors during initial page load.

**Solution:** Time rendering moved to client-side using `useState` + `useEffect` pattern with 60-second auto-update interval.

**Impact:** Eliminates hydration warnings, improves initial page load stability.

### ✅ WebSocket Error Handling Enhancement
Implemented comprehensive error logging and intelligent reconnection strategy.

**New Features:**
- **WebSocketErrorDetails Interface:** Captures type, timestamp, readyState, URL, and human-readable message
- **Exponential Backoff:** Reconnection delay: `min(3s * 2^attempt, 30s)`
- **Graceful Degradation:** Auto-switches to REST API after 3 consecutive WebSocket failures
- **Lifecycle Management:** `disable()`, `enable()`, and `isWebSocketDisabled()` methods

**Impact:** Users see detailed error information, and system maintains functionality via REST fallback when WebSocket is unavailable.

### ✅ Component Cleanup
Removed dead code from ChatMessage component for improved maintainability and bundle size.

**Changes:**
- Removed unused imports: `ThinkingState`, `useChatStore`, `isThinking`
- ChatMessage now serves as pure presentation component
- Thinking state logic correctly delegated to parent `ChatMessages` component

**Impact:** Cleaner code architecture, reduced bundle size, improved component modularity.

---| `Confidence Ring showing wrong colors` | Fixed in v1.0.1 - update to latest version |
| `React hydration error on chat header` | Fixed in v1.0.1 - update to latest version |
| `WebSocket empty error in console` | Fixed in v1.0.1 - system auto-switches to REST fallback |

---

## 📖 Documentation

| Guide | Description | Link |
|-------|-------------|-------|
| **Architecture Deep-Dive** | System design, data flows, design decisions | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **Contributing Guide** | First-time contributor, code style, PR process | [CONTRIBUTING.md](docs/CONTRIBUTING.md) |
| **API Reference** | All endpoints, schemas, examples | `/docs` (when running) |
| **Deployment Guide** | Production deployment, scaling, security | [DEPLOYMENT.md](docs/DEPLOYMENT.md) |
| **Troubleshooting** | Common issues and solutions | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| **RAG Evaluation** | Quality metrics, testing methodology | [docs/RAG_EVALUATION.md](docs/RAG_EVALUATION.md) |

---

## 🤝 Contributing

We ❤️ contributions! Whether you're fixing bugs, adding features, improving documentation, or reporting issues—every contribution helps.

### 🌟 First-Time Contributors

New to open source? We've made it easy:

1. **Find a "Good First Issue"**: Look for issues labeled `good first issue`
2. **Join Our Community**: [GitHub Discussions](https://github.com/nordeim/singapore-smb-support-agent/discussions)
3. **Ask Questions**: No question is too simple! We're here to help

### 🚀 Quick Contribution Setup

```bash
# 1. Fork & Clone
git clone https://github.com/nordeim/singapore-smb-support-agent.git
cd singapore-smb-support-agent

# 2. Create Feature Branch
git checkout -b feature/your-feature-name

# 3. Make Changes & Test
docker compose up -d  # Services running
pytest  # Run tests

# 4. Commit & Push
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name

# 5. Open Pull Request
# Visit GitHub and click "Compare & pull request"
```

### 📋 Contribution Types We Welcome

| Type | Example | Level |
|------|---------|--------|
| **Bug Fixes** | Fix broken ingestion pipeline | 🟢 Beginner |
| **Features** | Add new RAG retrieval strategy | 🟡 Intermediate |
| **Documentation** | Improve API docs, add examples | 🟢 Beginner |
| **Tests** | Increase test coverage | 🟢 Beginner |
| **Performance** | Optimize Qdrant queries | 🔴 Advanced |
| **Internationalization** | Add new language | 🟡 Intermediate |

### 🎨 Code Style & Standards

```bash
# Format code
cd backend && ruff format .
cd frontend && npm run format

# Lint code
cd backend && ruff check .
cd frontend && npm run lint

# Type check
cd backend && mypy app/
cd frontend && npx tsc --noEmit
```

**Required Standards:**
- Python: Black formatter, Ruff linter, MyPy types
- JavaScript/TypeScript: Prettier, ESLint
- Tests: 80% coverage minimum for new code
- Docs: Docstrings for all public functions

### 📝 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] All tests pass (`pytest`)
- [ ] Code follows style guide
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] PR description includes:
  - [ ] What changed
  - [ ] Why it's needed
  - [ ] How you tested it
  - [ ] Screenshots (if UI change)

---

## 🗺️ Roadmap

### ✅ Completed (v1.0)
- [x] Core RAG pipeline
- [x] Hierarchical memory system
- [x] PDPA compliance features
- [x] Multi-doc ingestion
- [x] Real-time WebSocket chat
- [x] Auto-escalation logic

### 🚧 In Progress (v1.1)
- [ ] Multi-language support (Chinese, Malay, Tamil)
- [ ] Advanced analytics dashboard
- [ ] A/B testing for prompts
- [ ] Enhanced evaluation suite

### 📋 Planned (v1.2)
- [ ] Voice input/output support
- [ ] WhatsApp integration
- [ ] Custom model fine-tuning
- [ ] Customer sentiment tracking over time
- [ ] Automated follow-up workflows

### 🌟 Future Vision
- [ ] Multi-tenant SaaS deployment
- [ ] White-label customization
- [ ] Mobile apps (iOS/Android)
- [ ] AI-powered knowledge base suggestions
- [ ] Community knowledge sharing

**Want to help?** Pick an issue from [Good First Issues](https://github.com/nordeim/singapore-smb-support-agent/labels/good%20first%20issue) or propose a new one!

---

## 📊 Project Stats

| Metric | Value |
|--------|--------|
| **Language** | Python, TypeScript |
| **Lines of Code** | ~15,000+ |
| **Test Coverage** | 75%+ (target: 80%) |
| **Dependencies** | 25+ production |
| **Docker Images** | 4 services |
| **Supported Formats** | 10+ document types |
| **Response Time (p50)** | < 1.5s |
| **Concurrent Users** | 100+ |

---

## 🎓 Use Cases

### 1. E-commerce Support

**Challenge:** Handle 500+ daily customer queries about orders, returns, shipping

**Solution:**
- RAG retrieves from FAQ + Policies + Order History
- Auto-escalates complex disputes to humans
- 30-day conversation memory for context

### 2. Professional Services

**Challenge:** Consultants need AI to answer client questions about services, pricing, SLA

**Solution:**
- Ingest service catalog + contract terms
- PDPA-compliant client data handling
- Meeting scheduler integration (future)

### 3. Healthcare (Simplified)

**Challenge:** Clinic needs to answer appointment, insurance, procedure questions

**Solution:**
- Strict HIPAA-like compliance (customizable)
- Multi-language for Singapore context
- Emergency detection & immediate escalation

---

## 🔗 Resources

### 📖 Learning Resources
- [RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) - LangChain RAG guide
- [Qdrant Documentation](https://qdrant.tech/documentation/) - Vector DB best practices
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) - Backend framework

### 🌐 Community
- [GitHub Discussions](https://github.com/nordeim/singapore-smb-support-agent/discussions) - Ask questions, share ideas
- [Contributors](https://github.com/nordeim/singapore-smb-support-agent/graphs/contributors) - Meet the team

### 📧 Support
- 🐛 [Report Bugs](https://github.com/nordeim/singapore-smb-support-agent/issues/new?template=bug_report.md)
- 💡 [Request Features](https://github.com/nordeim/singapore-smb-support-agent/issues/new?template=feature_request.md)
- 📚 [Documentation Issue](https://github.com/nordeim/singapore-smb-support-agent/issues/new?template=documentation.md)

---

## ⚖️ License

MIT License - see [LICENSE](LICENSE) for details.

**Commercial Use?** Yes, free to use and modify. Attribution appreciated but not required.

---

<div align="center">

### Built with ❤️ for Singapore SMBs

[![Star on GitHub](https://img.shields.io/github/stars/nordeim/singapore-smb-support-agent?style=social)](https://github.com/your-org/singapore-smb-support-agent/stargazers)
[![Fork on GitHub](https://img.shields.io/github/forks/your-org/singapore-smb-support-agent?style=social)](https://github.com/your-org/singapore-smb-support-agent/network/members)

**⭐ If this project helps you, please consider starring it!**

</div>
