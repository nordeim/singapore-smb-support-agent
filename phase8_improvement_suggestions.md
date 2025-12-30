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

---

Above is an exceptional set of improvements. You have accurately identified the gap between "Functional" (standard library implementation) and "Avant-Garde" (bespoke, trust-centric UX).

The proposed direction aligns perfectly with the **Singapore SMB context**: it prioritizes **clarity, density, and verification** over softness and abstraction.

Below is my meticulous critique and refinement of your suggestions against my architectural standards, followed by the consolidated **Avant-Garde Execution Roadmap**.

### 1. Critique & Analysis of Suggestions

| Feature | Your Suggestion | My Analysis & Refinement |
| :--- | :--- | :--- |
| **Aesthetic Direction** | **"Utilitarian Elegance"** (High contrast, sharp radius, Manrope/Inter). | **Status: APPROVED.** <br> **Critique:** Sharp borders (`radius-sm` or `0px`) convey precision, fitting for a business tool. **Refinement:** We will use `zinc-950` for text and `zinc-100` for subtle backgrounds to avoid the "harsh pure black" while maintaining high contrast. |
| **Cognitive Transparency** | **"Optimistic Thought Stream"** (Visualizing scanning/cross-referencing). | **Status: REFINED.** <br> **Critique:** Excellent for perceived latency reduction. <br> **Technical Reality:** Since we cannot guarantee the backend emits specific "tool start" events via WebSocket in the current MVP, we will implement a **Heuristic Simulation**. The UI will cycle through `Scanning Knowledge Base...` → `Verifying Policy...` → `Formatting Response...` based on typical latency curves (0-2s), clearing instantly when the first token arrives. |
| **Citations Layout** | **"Hybrid Layout"** (Left Answer / Right Evidence). | **Status: MODIFIED for Responsive.** <br> **Critique:** A fixed split-pane (Left/Right) breaks on mobile, where many SMB owners operate. <br> **Refinement:** We will use an **"Interactive Citation Drawer."** Citations appear as inline badges `[1]` in the text. Clicking one opens a **Sheet (Side Drawer)** on desktop or a **Bottom Sheet** on mobile. This preserves the clean chat aesthetic while offering deep-dive capability. |
| **Trust Meter** | **"Trust Meter"** (Confidence visualization). | **Status: APPROVED.** <br> **Refinement:** We will use a **micro-interaction ring** around the bot avatar. <br> Green = >85%, Amber = 70-85%, Red/Hollow = <70%. This avoids cluttering the message bubble while keeping the status omnipresent. |
| **PDPA UI** | **"Active Compliance"** (Timers/Wipe controls). | **Status: APPROVED.** <br> **Refinement:** We will place a **"Session Pulse"** in the header—a subtle countdown indicator that turns red when the session is near expiry (30m limit). |

---

### 2. Consolidated Avant-Garde Execution Roadmap

Based on the alignment of our visions, here is the technical roadmap I will execute. This moves us from "Phase 8 Planning" to "Phase 8 Execution."

#### Phase 8.1: The "Singapore Business" Visual System
*   **Typography:** Install `@fontsource/manrope` (Headings) and `@fontsource/inter` (Body).
*   **Variables:** Overhaul `globals.css`.
    *   Eliminate "soft" shadows. Replace with **1px borders** (`border-zinc-200`).
    *   Set global `radius` to `0.125rem` (2px).
    *   Define "Trust Colors": `semantic-green` (Verified), `semantic-amber` (Warning), `navy-900` (Primary Brand).

#### Phase 8.2: Component Architecture (The "Transparency Layer")
*   **`ThinkingState.tsx`:** A dedicated component for the "Heuristic Thought Stream."
*   **`CitationBadge.tsx`:** A clickable inline component for `[1]`, `[2]`.
*   **`EvidenceSheet.tsx`:** The Shadcn `Sheet` component repurposed to display raw RAG source chunks when a citation is clicked.

#### Phase 8.3: The "Cognitive" Chat Interface
*   **`ChatMessage.tsx` Overhaul:**
    *   **Header:** Bot Avatar + Confidence Ring + Timestamp.
    *   **Body:** Markdown renderer with custom components for lists/tables (dense data display).
    *   **Footer:** "Verified Sources" list (collapsible).
*   **`ChatInput.tsx` Redesign:**
    *   Transform from "Message Bar" to "Inquiry Console."
    *   Include quick-action chips: "Check Pricing", "Business Hours", "Policy Check".

---

### 3. Implementation Trigger

I have full context. I do **not** need to write from scratch; I will utilize the existing `shadcn` foundation but will **heavily modify** the component logic and CSS variables to achieve this vision.

**I will now proceed to Phase 8.1 and 8.2: Establishing the Visual System and Building the Transparency Components.**

Begin by installing the specific font dependencies and configuring the `globals.css` for the "Utilitarian" aesthetic?
