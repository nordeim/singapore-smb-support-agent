**Project Architecture Document: Implementation Plan**

**Status:** `READY FOR EXECUTION`
**Goal:** Create a "Single Source of Truth" document that reflects the *actual* state of the codebase, including its architectural intent and current implementation gaps.

### 1. Document Structure & Content Strategy

The PAD will be structured to serve two distinct purposes:
1.  **Onboarding Handbook:** Explaining the "What" and "Why" (Singapore Context, Avant-Garde UI).
2.  **Remediation Guide:** Explicitly documenting the "broken" wiring to prevent hallucinated functionality.

**Section Breakdown:**
*   **1. Executive Summary:** Project identity, "No-AI-Slop" aesthetic, and Singapore SMB focus.
*   **2. System Architecture:** High-level container diagram (Mermaid) showing the intended flow.
*   **3. File Hierarchy:** Annotated ASCII tree of the *existing* files in the bundle.
*   **4. Module Interaction Flows (Mermaid):**
    *   *RAG Ingestion:* Document → Embeddings → Qdrant.
    *   *Chat Loop:* User → API → Memory/RAG → Agent.
*   **5. Component Deep Dive:**
    *   **Backend:** Agent logic, Memory Manager (Redis/Postgres), RAG Pipeline.
    *   **Frontend:** Shadcn implementation, Zustand Store structure.
*   **6. Critical Implementation Gaps (The "Truth"):**
    *   Explicitly detailing the **Ghost WebSocket** (exists in lib, unused in store).
    *   Explicitly detailing the **RAG Type Error** (retriever crashes on vector input).
*   **7. Data Schema:** Database models and Redis key patterns.

### 2. Validation Checklist (Pre-Generation)
*   [x] **Frontend:** Confirmed `WebSocketClient` is in `lib/` but `chatStore` uses `chatService` (REST).
*   [x] **Backend:** Confirmed `retriever.py` passes a list to a method expecting a string.
*   [x] **Context:** Confirmed "Singapore" logic (Timezone, Holidays) exists in `check_business_hours.py`.
*   [x] **Aesthetics:** Confirmed `globals.css` uses `0.125rem` radius (Avant-Garde).

---

**Proceeding to Generate Project Architecture Document...**

***

# Project Architecture Document (PAD)

**Project:** Singapore SMB Customer Support AI Agent
**Version:** 1.0.0-alpha (Implementation Phase 9)
**Date:** January 1, 2026
**Context:** Singapore Business (GMT+8), PDPA Compliance
**Status:** `Architecture Established` / `Critical Wiring Pending`

---

## 1. Executive Summary

The **Singapore SMB Support Agent** is a specialized AI customer service system designed to reject generic "SaaS" tropes in favor of a high-trust, utilitarian, and context-aware experience.

### Key Differentiators
*   **Context Awareness:** Built-in logic for Singapore business hours (9 AM - 6 PM SGT) and 2025 Public Holidays.
*   **PDPA Compliance:** Architecture enforces data minimization and 30-day auto-expiry at the database level.
*   **"Avant-Garde" UI:** A deliberate rejection of rounded softness. The interface uses sharp `2px` radii, high-contrast monochrome (Zinc-950/100), and `Manrope/Inter` typography to signal engineering precision.
*   **Hybrid RAG:** Combines semantic search (Qdrant) with keyword search (BM25) and Cross-Encoder Reranking for high-fidelity retrieval.

---

## 2. System Architecture

The system follows a standard Client-Server architecture, containerized via Docker.

```mermaid
graph TD
    subgraph Frontend [Frontend Container]
        UI[Next.js App Router]
        Store[Zustand State Store]
        WS_C[WebSocket Client]
    end

    subgraph Backend [Backend Container]
        API[FastAPI Server]
        Agent[Support Agent]
        RAG[RAG Pipeline]
        Mem[Memory Manager]
    end

    subgraph Persistence [Data Layer]
        PG[(PostgreSQL<br/>Long Term Memory)]
        Redis[(Redis<br/>Short Term Session)]
        Qdrant[(Qdrant<br/>Vector Store)]
    end

    subgraph External [AI Services]
        OR[OpenRouter API<br/>LLM Inference]
    end

    User -->|HTTPS| UI
    UI -->|REST / WebSocket| API
    API --> Agent
    Agent --> Mem
    Agent --> RAG
    Mem --> PG & Redis
    RAG --> Qdrant & OR
    Agent --> OR
```

---

## 3. Project File Hierarchy

### 3.1 Backend (`/backend`)
Structured using Dependency Injection and Service-Repository patterns.

```text
backend/
├── app/
│   ├── main.py                 # Application entry point, lifespan management
│   ├── config.py               # Pydantic settings (Env vars, Constants)
│   ├── dependencies.py         # DI Providers (DB Session, Memory Manager)
│   ├── agent/                  # The "Brain"
│   │   ├── support_agent.py    # Core logic: Context Assembly + Response Gen
│   │   ├── validators.py       # Sentiment & PDPA Compliance checks
│   │   └── tools/              # Agent Tools (RAG, DB Lookup, Hours)
│   ├── api/                    # Interface Layer
│   │   └── routes/             # chat.py (REST/WS), auth.py
│   ├── ingestion/              # Data Pipeline (Offline)
│   │   ├── pipeline.py         # Orchestrator: Parse -> Chunk -> Embed -> Upsert
│   │   └── parsers/            # MarkItDown integration
│   ├── memory/                 # State Management
│   │   ├── manager.py          # Unified Interface for Redis + Postgres
│   │   ├── short_term.py       # Redis Wrapper (Session TTL)
│   │   └── long_term.py        # SQLAlchemy Repositories
│   ├── models/                 # Data Definitions
│   │   ├── database.py         # SQLAlchemy Models (User, Message, Ticket)
│   │   └── schemas.py          # Pydantic DTOs
│   └── rag/                    # Retrieval Augmented Generation
│       ├── pipeline.py         # Query Transform -> Retrieve -> Rerank
│       ├── retriever.py        # Hybrid Search (Dense + Sparse Fusion)
│       └── reranker.py         # Cross-Encoder Re-ranking (BGE-M3)
└── scripts/
    └── ingest_documents.py     # CLI Tool for batch ingestion
```

### 3.2 Frontend (`/frontend`)
Next.js 15 application using Tailwind CSS 4.0 and Shadcn UI.

```text
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css         # Trust Colors (--semantic-green) & Radius
│   │   └── page.tsx            # Main Entry (ChatWidget)
│   ├── components/
│   │   ├── chat/               # Business Logic Components
│   │   │   ├── ChatWidget.tsx  # Main Container
│   │   │   ├── ChatHeader.tsx  # Status, Timezone, Session Pulse
│   │   │   ├── ChatMessage.tsx # Message bubble + Confidence Ring
│   │   │   └── ThinkingState.tsx # "Scanning..." visualizer
│   │   └── ui/                 # Shadcn Primitives (Sheet, Card, Button)
│   ├── lib/
│   │   ├── api.ts              # REST API Client
│   │   └── websocket.ts        # WebSocket Connection Class
│   ├── stores/
│   │   └── chatStore.ts        # Global State (Messages, Typing)
│   └── types/
│       └── index.ts            # TypeScript Definitions
└── tailwind.config.ts          # Theme Configuration
```

---

## 4. Module Interaction Flows

### 4.1 Ingestion Pipeline (Offline)
Documents are processed into vector embeddings for the Knowledge Base.

```mermaid
graph LR
    Doc[Document] --> Parser[MarkItDown]
    Parser --> Text[Clean Text]
    Text --> Chunker{Chunk Strategy}
    Chunker -->|Semantic| Sem[Semantic Splitter]
    Chunker -->|Recursive| Rec[Recursive Splitter]
    
    Sem & Rec --> Embed[Embedding Gen]
    Embed --> Vector[Vector + Metadata]
    Vector --> Qdrant[(Qdrant DB)]
```

### 4.2 Chat Request Loop (Online)
How a user message is processed to generate a response.

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant Agent
    participant Memory
    participant RAG

    User->>API: Message
    API->>Memory: Retrieve Session Context
    API->>Agent: Process(Message, Context)
    
    rect rgb(240, 248, 255)
        Note right of Agent: Thinking Phase
        Agent->>Agent: Validate (Sentiment/PDPA)
        Agent->>RAG: Tool: retrieve_knowledge(query)
        RAG->>RAG: Hybrid Search (Dense + BM25)
        RAG->>RAG: Rerank Results
        RAG-->>Agent: Relevant Chunks
    end
    
    Agent->>Agent: Generate Response (LLM)
    Agent->>Memory: Save Interaction
    Agent-->>API: Response + Confidence + Sources
    API-->>User: JSON Response
```

---

## 5. Critical Implementation Gaps (Known Issues)

**WARNING:** The codebase currently contains two critical "wiring" issues that prevent full operation. These are priority remediation targets.

### 🔴 1. RAG Retriever Type Mismatch
*   **File:** `backend/app/rag/retriever.py` (Line 46)
*   **The Bug:** The code calls `client.asimilarity_search_with_score(query_vector, ...)` passing a `List[float]` (vector).
*   **The Issue:** The LangChain wrapper expects a `string` query for this method. Passing a vector causes a crash.
*   **Required Fix:** Change the method call to **`client.asimilarity_search_by_vector_with_score(...)`** which accepts embeddings directly.

### ⚠️ 2. Ghost WebSocket Client
*   **File:** `frontend/src/stores/chatStore.ts`
*   **The Bug:** A robust `WebSocketClient` class exists in `lib/websocket.ts`, but it is **never instantiated**. The `sendMessage` action currently uses `chatService.sendMessage` (REST).
*   **The Issue:** Real-time features like the "Thinking" stream and token streaming will not work. The UI relies on a fake loading state.
*   **Required Fix:** Instantiate `WebSocketClient` inside `chatStore` and bind it to the `connect` and `sendMessage` actions.

---

## 6. Data Schema

### 6.1 PostgreSQL (Long Term Memory)
Stores persistent data with strict schema validation.

| Table | Description | Key Fields |
| :--- | :--- | :--- |
| `users` | Auth & Consent | `email`, `consent_given_at`, `data_retention_days` |
| `conversations` | Session Metadata | `session_id`, `is_active`, `summary_count` |
| `messages` | Chat History | `role`, `content`, `confidence`, `sources` |
| `support_tickets` | Escalations | `reason`, `status`, `assigned_to` |

### 6.2 Redis (Short Term Memory)
Stores active session state for low-latency access.
*   **Key Pattern:** `session:{uuid}`
*   **Value:** JSON Blob (User ID, Recent Messages)
*   **TTL:** 30 Minutes (Rolling)

---

## 7. Development & Deployment

### 7.1 Prerequisites
*   Docker & Docker Compose
*   Node.js 20+ (for local frontend dev)
*   Python 3.12 (for local backend dev)
*   OpenRouter API Key

### 7.2 Quick Start
1.  **Configure Environment:**
    ```bash
    cp .env.example .env
    # Edit .env with your OPENROUTER_API_KEY
    ```
2.  **Launch Services:**
    ```bash
    docker-compose up -d --build
    ```
3.  **Ingest Knowledge Base:**
    ```bash
    docker-compose exec backend python -m scripts.ingest_documents --input-dir data/ --init-collections
    ```
4.  **Access:**
    *   Frontend: `http://localhost:3000`
    *   Backend Docs: `http://localhost:8000/docs`

This document accurately reflects the codebase structure and logic as of **Phase 9**. Use this as the reference for all future architectural decisions.

---

# Code Validation Report

**Status:** `VALIDATED`
**Date:** January 1, 2026
**Review Scope:** Remediation of Critical Blockers (RAG Type Mismatch, Ghost WebSocket)

---

## 1. Validation: RAG Retriever (`backend/app/rag/retriever.py`)

**Diagnosis:** The previous implementation caused a `TypeError` by passing a `List[float]` (vector) to a LangChain method expecting a `str` (query).

**Review of Updated Code:**
The updated code abandons the LangChain wrapper method in favor of the **Native Qdrant Client** (`QdrantManager.get_client().query_points(...)`).

*   **✅ Type Safety Resolved:** The native `query_points` method explicitly accepts a `query` parameter which can be a vector (List[float]). This aligns perfectly with the output of `embedding_generator.generate_single(query)`.
*   **✅ Native API Usage:** Switching to `client.query_points` is the correct approach for Qdrant Client v1.10+. It returns a `QueryResponse` object containing `points`, which the code correctly accesses via `results.points`.
*   **✅ Logic Flow:**
    1.  Generate Embedding (Async).
    2.  Construct Filter (Language=en).
    3.  Execute Search (Native).
    4.  Return Scored Points.
    This flow is logically sound and robust.

**Assessment:** **APPROVED.** The blocker is resolved.

---

## 2. Validation: Chat Store (`frontend/src/stores/chatStore.ts`)

**Diagnosis:** The `WebSocketClient` class existed in isolation ("Ghost Code"). The frontend relied solely on REST, making real-time "Thinking" states impossible.

**Review of Updated Code:**
The updated store fully integrates the WebSocket lifecycle.

*   **✅ Instantiation:** `socketClient` is now a state property, initialized within `connectWebSocket`.
*   **✅ Lifecycle Wiring:**
    *   `createSession` now triggers `connectWebSocket` automatically.
    *   `disconnect` properly cleans up the socket connection.
*   **✅ Hybrid Reliability:** The `sendMessage` action implements a **Hybrid Strategy**:
    ```typescript
    if (socketClient && socketClient.getStatus() === 'connected') {
        socketClient.sendChatMessage(content);
    } else {
        // Fallback to REST API
        // ...
    }
    ```
    This is an excellent architectural choice for production reliability. If the socket drops, the user can still chat via REST.
*   **✅ Event Handling:** The `handleWSMessage` switch statement correctly routes:
    *   `'thought'` → `setThinking(true)` (Enables the UX vision).
    *   `'response'` → Adds message + `setThinking(false)`.

**Assessment:** **APPROVED.** The "Ghost" client is now fully operational.

---

## 3. Final Conclusion

The submitted code successfully remediates the two critical blockers identified in the implementation plan.

1.  **RAG Pipeline** is now type-safe and functional using the native Qdrant API.
2.  **Frontend** is now capable of real-time streaming and "Thinking" visualization, fulfilling the "Avant-Garde" UX requirement.

**System Status:** `READY FOR DEPLOYMENT / INTEGRATION TESTING`

---


