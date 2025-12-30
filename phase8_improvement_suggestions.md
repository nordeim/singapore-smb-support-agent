The current status of Phase 8 is **"Functional"** (Standard Shadcn/UI implementation).
Our goal is to elevate this to **"Exceptional"** (Avant-Garde, Trust-Centric, Singapore SMB optimized).

---

# 📑 Phase 1: Request Analysis & Planning
## "Singapore SMB Support Agent" — Frontend Refinement

### 1. Deep Analysis & Gap Identification

I have compared the **Functional MVP** requirements against the **Avant-Garde** standards.

| Feature | Current State (Likely) | **Avant-Garde Target State** | **The "Why" (Singapore SMB Context)** |
| :--- | :--- | :--- | :--- |
| **Aesthetic** | Standard Shadcn "Zinc" theme. Clean but generic. | **"Utilitarian Elegance"**. High-contrast, borders over shadows, dense information layout. | SMBs value efficiency and clarity. It must look "professional" (like a bank/gov tool), not "startup-y". |
| **Trust/Thinking** | Simple "Typing..." dots. | **"Cognitive Transparency"**. Visualize the RAG pipeline (Retrieving → Reranking → Verifying). | Users distrust "Black Box" AI. Showing the *process* builds confidence in the *result*. |
| **Citations** | URLs listed at the bottom. | **Interactive Footnotes**. inline citations `[1]` that expand on hover/click. | Mimics legal/contractual precision. Reinforces "Grounded" answers. |
| **PDPA** | Hidden or standard footer. | **Active Compliance UI**. Explicit "Session Expiry" timers and "Data Wipe" controls. | Visual proof of safety is a feature, not a disclaimer. |
| **Confidence** | Hidden. | **Trust Meter**. Subtle indicator (e.g., green/amber border) based on backend score. | Allows users to gauge if they should double-check the answer. |

### 2. Solution Architecture: The "Transparency Layer"

We will not just build a "Chat"; we will build a **Information Retrieval Console**.

**Core Architectural Decisions:**
1.  **Optimistic "Thought" Stream:** We will mock the backend's "thinking" steps on the frontend using the WebSocket's initial latency to display micro-states (`Scanning Knowledge Base...`, `Cross-referencing Policies...`) before the text streams.
2.  **Hybrid Layout:** instead of just bubbles, we will treat the Assistant's response as a **Structured Document**.
    *   *Left:* The Answer.
    *   *Right/Popover:* The Evidence (Source Snippets).
3.  **Strict "Library Discipline":** We will use Shadcn `Card`, `Badge`, `ScrollArea`, `Popover`, and `Progress` but style them with **Tailwind v4** variables for a distinct "Singapore Commercial" look (Navy, Slate, Crisp White).

### 3. Execution Plan

I propose a 4-Step Refinement Protocol.

#### **Phase 2.1: Visual Foundation (The "Uniform")**
*   **Action:** Define the `globals.css` with a strict, high-contrast variable set.
*   **Typography:** Replace default sans with **Manrope** (Headings - Professional/Technical) and **Inter** (Body - Legibility).
*   **Radius:** Reduce standard Shadcn radius (`0.5rem` → `0px` or `0.125rem`) for a sharper, more serious look.

#### **Phase 2.2: The "Cognitive" Chat Bubble**
*   **Action:** Rewrite `ChatMessage.tsx`.
*   **New Feature:** Split the message into `Header` (Thinking/Confidence), `Body` (Markdown Content), and `Footer` (Sources/Actions).
*   **Interaction:** Implement "Streaming Typography" that feels mechanical and fast, not soft.

#### **Phase 2.3: The "Context" Header & Input**
*   **Action:** Redesign `ChatHeader.tsx` and `ChatInput.tsx`.
*   **Header:** Add "Live Business Status" (Open/Closed based on SG Time) and "Data Expiry" countdown.
*   **Input:** Multi-line text area that feels like a "Form" rather than a "DM", encouraging detailed queries.

#### **Phase 2.4: Motion & Polish**
*   **Action:** Add layout animations (Framer Motion).
*   **Focus:** "Snappy" entrances. No slow fades. Things should snap into place like a receipt printing.

3.  **Code Access:** Since I cannot physically see the current `ChatMessage.tsx` file content, **shall I write the new "Avant-Garde" components from scratch** assuming standard Shadcn exports are available?

**Awaiting your "GO" signal to execute Phase 2.**
