# AGENT.md

**Project:** Singapore SMB Customer Support AI Agent
**Version:** 1.0.1 (Production Ready)
**Last Updated:** January 1, 2026
**Context:** Singapore Business (GMT+8) | PDPA Compliant | Hybrid RAG

---

## 1. THE EXECUTIVE MANDATE
**"We do not build generic chatbots. We build instruments of trust."**

This project is a rejection of the "SaaS blob" aesthetic and "AI slop" logic. We are building a high-precision support tool for Singapore Small-to-Medium Businesses (SMBs).

### Core Design Philosophy
1.  **Avant-Garde Utilitarianism:**
    *   **Radius:** Strict `2px` (`0.125rem`). No soft `8px` rounded corners.
    *   **Typography:** `Manrope` (Headings) for authority, `Inter` (Body) for legibility.
    *   **Palette:** Zinc-950/100 monochrome base. Semantic colors used *only* for trust signaling.
2.  **Cognitive Transparency:**
    *   We do not hide latency; we visualize "thinking."
    *   We do not hide data retention; we visualize expiration.
    *   User Trust > Smooth Animation.
3.  **Regulatory Obsession (PDPA):**
    *   Data minimization is architectural, not just legal.
    *   Sessions expire hard at 30 minutes (Redis TTL).
    *   Consent is tracked immutably.

---

## 2. SYSTEM ARCHITECTURE

### 2.1 The Tech Stack
*   **Frontend:** Next.js 15 (App Router), React 18, Zustand, Tailwind CSS 3.4, Shadcn/Radix.
*   **Backend:** Python 3.12, FastAPI, Pydantic AI, SQLAlchemy (Async).
*   **Data Layer:**
    *   **Vector:** Qdrant (Native Client, Hybrid Search).
    *   **Relational:** PostgreSQL 16 (Audit, Tickets).
    *   **Cache:** Redis 7 (Session State, 30m TTL).
*   **AI/LLM:** OpenRouter (GPT-4o-mini primary), OpenAI Embeddings (`text-embedding-3-small`).

### 2.2 The File Map (Critical Paths)
*Do not touch files outside these paths without strong justification.*

```text
/backend
├── app/agent/support_agent.py    # BRAIN: Orchestration, Thought Emission
├── app/rag/retriever.py          # SEARCH: Native Qdrant Hybrid Search (Critical Fix applied)
├── app/memory/manager.py         # MEMORY: Redis + Postgres Coordination
├── app/memory/long_term.py       # DB: SQL Repositories (Ticket/User logic)
└── app/ingestion/pipeline.py     # ETL: MarkItDown -> Chunk -> Embed

/frontend
├── src/stores/chatStore.ts       # STATE: WebSocket/REST logic, Message handling
├── src/lib/websocket.ts          # COMMS: Reconnection logic, Error handling
├── src/components/chat/
│   ├── ChatWidget.tsx            # CONTROLLER: Layout
│   ├── ChatMessages.tsx          # VIEW: ThinkingState relocation logic
│   ├── ChatMessage.tsx           # ATOM: ConfidenceRing integration
│   └── SessionPulse.tsx          # COMPLIANCE: PDPA Countdown
└── src/app/globals.css           # VISUAL: HSL Semantic Variables
```

---

## 3. CRITICAL WORKFLOWS

### 3.1 The "Cognitive Transparency" Loop (WebSocket)
We stream the agent's internal state to the UI to build trust during latency.

1.  **Backend (`support_agent.py`):**
    *   `_emit_thought(session_id, "assembling_context")`
    *   `_emit_thought(session_id, "searching_knowledge")`
    *   `_emit_thought(session_id, "generating_response")`
2.  **Frontend (`chatStore.ts`):**
    *   Receives `type: "thought"`.
    *   Sets `isThinking: true`.
3.  **UI (`ChatMessages.tsx`):**
    *   Renders `<ThinkingState />` at the bottom of the list.
    *   **NOTE:** Do not nest this inside `ChatMessage`. It sits *between* messages.

### 3.2 The RAG Pipeline (Hybrid Search)
We use a sophisticated retrieval stack, not a basic wrapper.

1.  **Input:** User query.
2.  **Transform (`query_transform.py`):** Rewrites query for intent/keywords.
3.  **Retrieve (`retriever.py`):**
    *   **Dense:** OpenAI Embeddings (Semantic).
    *   **Sparse:** BM25 via Qdrant (Keyword).
    *   **Protocol:** Uses `client.query_points()` (Native API). **NEVER** use LangChain's `similarity_search` wrapper here (Type Mismatch risk).
4.  **Rerank (`reranker.py`):** Cross-Encoder (`BAAI/bge-reranker`) rescores top 50 -> top 5.

### 3.3 The Memory Hierarchy & PDPA
1.  **Hot Storage (Redis):** Active session.
    *   **TTL:** Hard set to 30 minutes.
    *   **Frontend:** `SessionPulse.tsx` visualizes this countdown using `sessionExpiresAt`.
2.  **Cold Storage (Postgres):** Audit logs.
    *   **Logic:** `update_ticket_status` must commit explicitly.
3.  **Compression:**
    *   Trigger: 20 messages.
    *   Action: LLM summarizes history into vector storage.

---

## 4. UI/UX CODING STANDARDS

### 4.1 The Visual System
*   **Colors (Trust-Based):**
    *   Use semantic classes: `ring-trust-green`, `bg-trust-amber`, `text-trust-red`.
    *   **NEVER** use `green-500` or generic Tailwind colors for status.
    *   **Source:** `globals.css` (Must use HSL syntax: `120 45% 69%`, not RGB).
*   **Components:**
    *   `ConfidenceRing`: Visualizes AI confidence (Green >85%, Amber >70%, Red <70%).
    *   `EvidenceSheet`: Shadcn Sheet showing raw RAG sources.
    *   `CitationBadge`: Inline `[1]` clickable triggers.

### 4.2 Frontend Pattern Constraints
*   **Library Discipline:** Use Shadcn/Radix primitives. Do not build custom modals.
*   **SSR Safety:** Time-based components (clocks, countdowns) must use `useState/useEffect` to avoid Hydration Mismatches.
*   **State:** Use `useChatStore` (Zustand).

---

## 5. OPERATIONAL PROTOCOLS

### 5.1 Environment
*   **Required:** `.env` in backend with `OPENROUTER_API_KEY`, `QDRANT_URL`, `DATABASE_URL`, `REDIS_URL`.
*   **Mocking:** If API keys are missing, the system may default to Mock Embeddings (check logs).

### 5.2 Deployment
*   **Docker:** `docker-compose up -d` handles PG, Redis, Qdrant, Backend.
*   **Frontend:** Run locally `npm run dev` or build container.
*   **Ingestion:** `docker-compose exec backend python -m scripts.ingest_documents --init-collections`

---

## 6. THE KILL LIST (Known Pitfalls)
*History must not repeat itself. These errors are strictly prohibited.*

1.  **The Phantom Update (Backend):**
    *   *Symptom:* DB updates (like Ticket Status) reflect in API response but revert on refresh.
    *   *Cause:* Returning data *before* `await db.commit()`.
    *   *Rule:* **Always** commit before returning in SQLAlchemy repositories.
2.  **The Invisible Color (Frontend):**
    *   *Symptom:* Trust rings appear transparent/black.
    *   *Cause:* `globals.css` variables defined as RGB (`100 100 100`) but Tailwind config expects `hsl()`.
    *   *Rule:* **Always** use valid HSL syntax (`120 50% 50%`) in CSS variables.
3.  **The Ghost WebSocket:**
    *   *Symptom:* Empty error logs, silent failures.
    *   *Cause:* Poor error serialization.
    *   *Rule:* Use the `WebSocketErrorDetails` interface in `websocket.ts`. Respect the exponential backoff logic.
4.  **RAG Type Mismatch:**
    *   *Symptom:* 500 Error during search.
    *   *Cause:* Passing `List[float]` vectors to LangChain methods expecting strings.
    *   *Rule:* Use `QdrantClient.query_points()` directly.

---

## 7. CURRENT STATUS
**State:** Production Ready (v1.0.1)
**Next Objectives:**
1.  Multilingual Support (Chinese/Malay).
2.  Advanced Analytics Dashboard.
3.  Voice Input Integration.

---

# Codebase Analysis Assessment Report

**Project:** Singapore SMB Customer Support AI Agent
**Version:** 1.0.1 (Codebase Audit)
**Date:** January 1, 2026
**Auditor:** Frontend Architect & Avant-Garde UI Designer

## 1. Executive Summary

The codebase demonstrates a high level of architectural maturity and strict adherence to the "Avant-Garde" design philosophy. The separation of concerns between `ingestion`, `rag`, `memory`, and `agent` modules is pristine. The frontend implements the requested "Utilitarian Elegance" with `2px` radii and correct semantic color usage.

However, a **Critical Logic Gap** was identified in the Agent's core processing logic. While the supporting infrastructure (RAG, Memory, WebSocket) is production-ready, the actual *response generation* logic in `SupportAgent` is currently a static placeholder/stub, effectively "lobotomizing" the AI. Additionally, a routing mismatch exists in the WebSocket configuration.

## 2. Implementation vs. Design Goals

| Feature | Design Goal | Actual Implementation | Status |
| :--- | :--- | :--- | :--- |
| **Visual Identity** | "Avant-Garde" (2px radius, Manrope/Inter). | **Perfect.** `globals.css` defines `--radius: 0.125rem` and `tailwind.config.ts` enforces it. | ✅ |
| **Trust Colors** | Semantic HSL variables (Green/Amber/Red). | **Verified.** `globals.css` uses valid HSL syntax (`120 45% 69%`), fixing previous RGB issues. | ✅ |
| **RAG Pipeline** | Hybrid Search (Dense + Sparse). | **Verified.** `HybridRetriever` uses native `qdrant_client` correctly. | ✅ |
| **Memory** | Hierarchical (Redis + Postgres). | **Verified.** `MemoryManager` correctly orchestrates dual-write and retention. | ✅ |
| **Agent "Brain"** | LLM-based generation using Pydantic AI. | **CRITICAL FAILURE.** The `SupportAgent` class contains hardcoded string templates instead of LLM calls. | ❌ |
| **Real-time** | WebSocket thought streaming. | **Implemented.** Infrastructure exists, but URL path is incorrect in frontend config. | ⚠️ |

## 3. Critical Findings ("The Kill List")

### 🔴 1. The "Lobotomized Agent" (Backend)
**File:** `backend/app/agent/support_agent.py`
**Method:** `_generate_response` (Lines 180-192)

**Analysis:**
The design calls for an LLM (GPT-4o) to synthesize the response. However, the current code is a mock implementation:
```python
def _generate_response(self, query: str, knowledge: str, context: AgentContext) -> str:
    """Generate response using system prompt and knowledge."""
    if knowledge:
        return f"""Based on our knowledge base, here's what I can help you with:\n\n{knowledge}..."""
    else:
        return """I couldn't find specific information..."""
```
**Impact:** The agent will **never** answer questions intelligently. It will simply regurgitate raw RAG chunks or apologize. The Pydantic AI integration described in the architecture is missing from this specific file.

### 🟠 2. WebSocket Route Mismatch (Frontend)
**File:** `frontend/src/stores/chatStore.ts` (Line 115) vs `backend/app/main.py`

**Analysis:**
*   **Backend:** Defines API prefix as `/api/v1` in `main.py`, and chat router as `/chat` with websocket at `/ws`.
    *   *Resulting URL:* `ws://localhost:8000/api/v1/chat/ws`
*   **Frontend:** Defaults to:
    ```typescript
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/chat/ws';
    ```
    *   *Resulting URL:* `ws://localhost:8000/chat/ws` (Missing `/api/v1`)
**Impact:** WebSocket connection will fail with `404 Not Found` in the default development environment unless the env var is manually corrected.

### 🟢 3. Phantom Update Fix Verification
**File:** `backend/app/memory/long_term.py`
**Analysis:** The previous "Phantom Update" bug (returning before commit) has been **verified as FIXED** in the provided file bundle.
```python
await self.db.commit() # Present before return
await self.db.refresh(ticket)
return ticket
```

---

## 4. Recommendations

1.  **Implant the Brain:** Immediately refactor `SupportAgent._generate_response` to initialize a `ChatOpenAI` client (or Pydantic AI Agent) and call `ainvoke` using the `RESPONSE_GENERATION_PROMPT`.
2.  **Fix Route Path:** Update `frontend/src/stores/chatStore.ts` default URL to include `/api/v1`.
3.  **Deploy:** Once #1 is fixed, the system is ready for UAT.

---

# AGENT.md

**Project:** Singapore SMB Customer Support AI Agent
**Version:** 1.0.2 (Remediation Pending)
**Context:** Singapore Business (GMT+8) | PDPA Compliant | Hybrid RAG

---

## 1. THE EXECUTIVE MANDATE
**"We do not build generic chatbots. We build instruments of trust."**

We are building a high-precision support tool for Singapore SMBs. Every pixel and every line of code must demonstrate:
1.  **Precision:** 2px border radius, strict typing, rigorous error handling.
2.  **Transparency:** Visualized thinking states, visualized data expiry.
3.  **Compliance:** Hard 30-minute session limits, strict data minimization.

---

## 2. SYSTEM ARCHITECTURE

### 2.1 The Tech Stack
*   **Frontend:** Next.js 15, Zustand, Tailwind CSS 3.4 (Semantic HSL).
*   **Backend:** FastAPI, Python 3.12, SQLAlchemy (Async).
*   **Intelligence:**
    *   **Vector:** Qdrant (Native Client, Hybrid Search).
    *   **LLM:** OpenRouter (GPT-4o-mini).
    *   **Orchestration:** Pydantic AI / LangChain.

### 2.2 Critical File Map
*Do not touch files outside these paths without justification.*

```text
/backend
├── app/agent/support_agent.py    # [CRITICAL] Needs LLM integration (currently stubbed)
├── app/rag/retriever.py          # SEARCH: Native Qdrant implementation
├── app/memory/long_term.py       # DB: SQL Repositories (Verified Fixed)
└── app/ingestion/pipeline.py     # ETL: MarkItDown -> Chunk -> Embed

/frontend
├── src/stores/chatStore.ts       # STATE: WebSocket Logic (Fix URL here)
├── src/components/chat/          # UI:
│   ├── ChatMessages.tsx          #   - Layouts thinking state
│   ├── ChatMessage.tsx           #   - Renders ConfidenceRing
│   └── SessionPulse.tsx          #   - Visualizes PDPA expiry
└── src/app/globals.css           # VISUAL: Semantic HSL Variables
```

---

## 3. OPERATIONAL LOGIC

### 3.1 The "Cognitive Transparency" Loop
We stream state to build trust.
1.  **Backend:** `SupportAgent` emits `thought` events via WebSocket.
2.  **Frontend:** `chatStore` catches events -> sets `isThinking` -> `ChatMessages` renders `<ThinkingState />`.
3.  **Visual:** "Scanning..." -> "Cross-referencing..." -> "Formatting...".

### 3.2 Hybrid RAG Pipeline
1.  **Retrieve:** `HybridRetriever` combines Dense (Vectors) + Sparse (BM25) via Qdrant.
2.  **Rerank:** `BGEReranker` (Cross-Encoder) selects top 5.
3.  **Compress:** `ContextCompressor` fits content into token budget.

### 3.3 PDPA & Memory
*   **Redis:** Stores active session. TTL hardcoded to 30 mins (`app/config.py`).
*   **Postgres:** Stores audit trail. `User.data_retention_days` defaults to 30.
*   **Frontend:** `SessionPulse` visualizes the Redis TTL.

---

## 4. IMMEDIATE ACTION ITEMS (The Fix List)

These are the blockers preventing Phase 10 (Testing/Dockerization):

1.  **Implement LLM Logic:**
    *   **File:** `backend/app/agent/support_agent.py`
    *   **Task:** Replace the mock string return in `_generate_response` with actual `ChatOpenAI` invocation using `RESPONSE_GENERATION_PROMPT`.
2.  **Correct WebSocket URL:**
    *   **File:** `frontend/src/stores/chatStore.ts`
    *   **Task:** Change default URL from `ws://localhost:8000/chat/ws` to `ws://localhost:8000/api/v1/chat/ws`.

---

## 5. CODING STANDARDS & PITFALLS

### Visual Standards
*   **Radius:** Always `rounded-lg` (maps to `0.125rem`/2px). Never use `rounded-xl`.
*   **Colors:** Use `trust.green`, `trust.amber`, `trust.red`. Never raw Tailwind colors.
*   **CSS:** Variables in `globals.css` must preserve HSL syntax (e.g., `120 45% 69%`).

### Backend Pitfalls
*   **The Phantom Update:** Always `await db.commit()` **before** returning data in `long_term.py`. (Currently fixed, do not regress).
*   **RAG Type Safety:** Never pass `List[float]` to LangChain's `similarity_search`. Use `qdrant_client.query_points` (Native API) as implemented in `retriever.py`.

---

*This document is the authoritative source for the Singapore SMB Support Agent codebase.*
