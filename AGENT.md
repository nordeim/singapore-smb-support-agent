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

*End of Briefing. You are now authorized to contribute.*
