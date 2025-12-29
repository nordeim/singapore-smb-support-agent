# Phase 8: Frontend Development - Implementation Plan

**Date**: 2025-12-29
**Status**: ⏳ PLANNING PHASE

---

## Executive Summary

Phase 8 involves creating the complete React/TypeScript frontend for the Singapore SMB Support Agent with Shadcn/UI components, WebSocket real-time communication, and Zustand state management.

---

## Current State Assessment

### ✅ Existing Infrastructure
- Next.js 15.1.0 with App Router
- React 18.3.1
- TypeScript 5.6.0
- Tailwind CSS 3.4.0
- Shadcn/UI configured with New York style
- Path aliases configured (@/components, @/lib, @/types, @/stores, @/hooks)

### ✅ Installed Dependencies
- `@radix-ui/react-avatar` ✅
- `@radix-ui/react-dialog` ✅
- `@radix-ui/react-scroll-area` ✅
- `@radix-ui/react-separator` ✅
- `@radix-ui/react-slot` ✅
- `@tanstack/react-query` ✅
- `zustand` ✅
- `clsx`, `tailwind-merge`, `tailwindcss-animate` ✅
- `lucide-react` ✅
- `date-fns` ✅

### ❌ Missing Dependencies (to install)
- `@radix-ui/react-label` (for form labels)
- `@radix-ui/react-toast` (for notifications)
- `@radix-ui/react-dropdown-menu` (optional, for menu)
- `class-variance-authority` (for component variants)
- `@/components/ui` directory (Shadcn/UI components)

### ⚠️ Files Present
- `src/app/page.tsx` - Placeholder page
- `src/app/layout.tsx` - Root layout
- `src/lib/utils.ts` - Utility function (cn)

---

## Phase 8 Task Breakdown (11 Tasks)

### Task 8.1: Install Shadcn/UI Components
**Status**: 📋 PLANNED

**Components to Install**:
- `button` - Primary action buttons
- `input` - Text input fields
- `label` - Form labels
- `toast` - Notification toasts
- `toast/use-toast` - Toast hook

**Commands**:
```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add toast
npx shadcn@latest add card
```

**Expected Output**: Files in `frontend/src/components/ui/`

---

### Task 8.2: Create TypeScript Types
**Status**: 📋 PLANNED

**File**: `frontend/src/types/index.ts`

**Types to Define**:
```typescript
// Message types
export type MessageRole = 'user' | 'assistant' | 'system'
export type Message = {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
  confidence?: number
  sources?: Source[]
}

// Source type
export type Source = {
  content: string
  metadata: Record<string, unknown>
  score: number
}

// Chat request/response
export type ChatRequest = {
  session_id: string
  message: string
  language?: string
}

export type ChatResponse = {
  session_id: string
  message: string
  role: string
  confidence: number
  sources: Source[]
  requires_followup: boolean
  escalated: boolean
  ticket_id?: string
}

// WebSocket types
export type WSMessage =
  | { type: 'connected'; session_id: string; message: string }
  | { type: 'response'; session_id: string; message: string; confidence: number; sources: Source[]; requires_followup: boolean; escalated: boolean; ticket_id?: string }
  | { type: 'error'; message: string }
  | { type: 'pong' }

export type WSMessageRequest =
  | { type: 'message'; message: string }
  | { type: 'ping' }
  | { type: 'disconnect' }

// Session/User types
export type Session = {
  session_id: string
  user_id?: number
  email?: string
  created_at: string
}

export type User = {
  id: number
  email: string
  is_active: boolean
  created_at: string
}

// Business hours type
export type BusinessHours = {
  is_open: boolean
  business_hours: string
  current_time: string
  timezone: string
}
```

---

### Task 8.3: Create API Client
**Status**: 📋 PLANNED

**File**: `frontend/src/lib/api.ts`

**Functions to Implement**:
```typescript
// Base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// Authentication
export const authService = {
  register: (email: string, password: string) => Promise<User>
  login: (email: string, password: string) => Promise<{ access_token: string }>
  logout: (session_id: string) => Promise<void>
  getCurrentUser: (session_id: string) => Promise<User>
  createSession: () => Promise<{ session_id: string; expires_in: string }>
}

// Chat API
export const chatService = {
  sendMessage: (session_id: string, message: string) => Promise<ChatResponse>
  getSession: (session_id: string) => Promise<{ session_id: string; messages: Message[] }>
}

// Health check
export const healthService = {
  check: () => Promise<{ status: string; services: Record<string, string> }>
}

// Error handling
export class APIError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message)
  }
}
```

---

### Task 8.4: Create WebSocket Client
**Status**: 📋 PLANNED

**File**: `frontend/src/lib/websocket.ts`

**Features to Implement**:
- WebSocket connection management
- Auto-reconnection with exponential backoff
- Heartbeat/ping-pong (30s interval)
- Message streaming
- Event callbacks (onMessage, onError, onClose, onOpen)
- Connection status tracking

**Interface**:
```typescript
export interface WebSocketClientOptions {
  url: string
  session_id: string
  onMessage?: (message: WSMessage) => void
  onError?: (error: Event) => void
  onClose?: (event: CloseEvent) => void
  onOpen?: () => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

export class WebSocketClient {
  connect(): void
  disconnect(): void
  send(message: WSMessageRequest): void
  getStatus(): 'connecting' | 'connected' | 'disconnected' | 'error'
}
```

---

### Task 8.5: Create Zustand Store (Chat Store)
**Status**: 📋 PLANNED

**File**: `frontend/src/stores/chatStore.ts`

**State to Manage**:
```typescript
interface ChatStore {
  // Session state
  sessionId: string | null
  isConnected: boolean
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'

  // Messages
  messages: Message[]
  isTyping: boolean

  // Actions
  setSessionId: (id: string) => void
  addMessage: (message: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  clearMessages: () => void
  setConnected: (connected: boolean) => void
  setConnectionStatus: (status: ChatStore['connectionStatus']) => void
  setTyping: (typing: boolean) => void

  // Async actions
  sendMessage: (content: string) => Promise<void>
  createSession: () => Promise<void>
  disconnect: () => void
}
```

---

### Task 8.6: Create ChatMessage Component
**Status**: 📋 PLANNED

**File**: `frontend/src/components/chat/ChatMessage.tsx`

**Features**:
- User message bubble (right-aligned, blue)
- Assistant message bubble (left-aligned, gray)
- Timestamp display
- Confidence indicator (if available)
- Source citations display (expandable)
- Markdown content rendering (if needed)
- Loading skeleton for pending messages

**UI Layout**:
```
┌──────────────────────────────────────┐
│ Assistant Message (left)             │
│ ┌──────────────────────────────┐   │
│ │ Message content               │   │
│ │ • Source 1 (0.95)          │   │
│ │ • Source 2 (0.88)          │   │
│ └──────────────────────────────┘   │
│ ⏰ 2:30 PM | Confidence: 0.92    │
└──────────────────────────────────────┘

                    ┌────────────┐
                    │ User Msg   │
                    │ (right)    │
                    └────────────┘
                        ⏰ 2:31 PM
```

---

### Task 8.7: Create ChatMessages Component
**Status**: 📋 PLANNED

**File**: `frontend/src/components/chat/ChatMessages.tsx`

**Features**:
- ScrollArea from Shadcn/UI
- Auto-scroll to bottom on new message
- Date separators (grouping messages by date)
- Typing indicator display
- Empty state (no messages)
- Message list from store

**Behavior**:
- Scrolls to bottom when new message added
- Maintains scroll position when viewing history
- Shows typing indicator at bottom when agent is responding

---

### Task 8.8: Create ChatInput Component
**Status**: 📋 PLANNED

**File**: `frontend/src/components/chat/ChatInput.tsx`

**Features**:
- Textarea (auto-expand)
- Send button (disabled when empty)
- Character count (optional, max: 5000)
- Enter key submit handling (Shift+Enter for newline)
- Focus management
- Loading state (disable while sending)

**UI Layout**:
```
┌──────────────────────────────────────────┐
│ ┌────────────────────────────────┐  ┌──┐│
│ │ Type your message here...     │  │Send││
│ └────────────────────────────────┘  └──┘│
│                                      │
│                     0/5000 characters │
└──────────────────────────────────────────┘
```

---

### Task 8.9: Create TypingIndicator Component
**Status**: 📋 PLANNED

**File**: `frontend/src/components/chat/TypingIndicator.tsx`

**Features**:
- 3-dot loading animation
- Fade in/out transitions
- "Agent is typing..." text
- Optional: Custom animation

**UI Layout**:
```
Agent is typing... ⚫⚫⚫
  ↑ 1 second interval
```

---

### Task 8.10: Create ChatWidget Component (Main Container)
**Status**: 📋 PLANNED

**File**: `frontend/src/components/chat/ChatWidget.tsx`

**Features**:
- Header with status and business hours
- Messages scroll area
- Input field with send button
- Typing indicator
- Connection status indicator
- Session management

**UI Layout**:
```
┌──────────────────────────────────────┐
│ 🟢 Singapore SMB Support  │
│ 🕐 Open: 9 AM - 6 PM (SGT)     │
├──────────────────────────────────────┤
│                                      │
│  ChatMessages Area (scrollable)       │
│                                      │
│  [Message 1 - Assistant]            │
│  [Message 2 - User]               │
│  [Message 3 - Assistant]            │
│                                      │
│  [Typing indicator... ⚫⚫⚫]    │
├──────────────────────────────────────┤
│ ┌────────────────────────────┐  ┌──┐│
│ │ Type your message...       │  │📤││
│ └────────────────────────────┘  └──┘│
└──────────────────────────────────────┘
```

---

### Task 8.11: Create ChatHeader Component
**Status**: 📋 PLANNED

**File**: `frontend/src/components/chat/ChatHeader.tsx`

**Features**:
- Status indicator (online/offline/closed)
- Business hours display
- Agent name
- Connection status badge
- Optional: Settings menu

**UI Layout**:
```
┌────────────────────────────────────┐
│ 🟢 Singapore SMB Support Agent   │
│ 🟢 Online • 9:00 AM - 6:00 PM  │
└────────────────────────────────────┘
```

**States**:
- 🟢 Online (business hours, connected)
- 🟡 Offline (outside business hours)
- 🔴 Error (connection failed)

---

## Implementation Order

### Phase 8.1: Foundation (Tasks 8.1-8.5)
1. Install Shadcn/UI components
2. Create TypeScript types
3. Create API client
4. Create WebSocket client
5. Create Zustand store

### Phase 8.2: UI Components (Tasks 8.6-8.9)
6. Create ChatMessage component
7. Create ChatMessages component
8. Create TypingIndicator component
9. Create ChatInput component

### Phase 8.3: Integration (Tasks 8.10-8.11)
10. Create ChatHeader component
11. Create ChatWidget component (main container)
12. Update main page.tsx to use ChatWidget

---

## Technical Requirements

### TypeScript Configuration
- Strict mode enabled ✅ (already configured)
- Path aliases ✅ (already configured)

### CSS/Styling
- Tailwind CSS classes
- Shadcn/UI styling (New York theme)
- Responsive design (mobile-first)
- Dark mode support (optional for MVP)

### Accessibility (WCAG AA)
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus management
- Screen reader support

### Browser Compatibility
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## File Structure After Phase 8

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx (updated with ChatWidget)
│   │   └── globals.css
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatWidget.tsx
│   │   │   ├── ChatHeader.tsx
│   │   │   ├── ChatMessages.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── TypingIndicator.tsx
│   │   └── ui/
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── toast.tsx
│   │       ├── use-toast.ts
│   │       ├── card.tsx
│   │       ├── avatar.tsx
│   │       ├── dialog.tsx
│   │       ├── scroll-area.tsx
│   │       └── separator.tsx (may exist)
│   ├── lib/
│   │   ├── utils.ts
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── stores/
│   │   └── chatStore.ts
│   └── types/
│       └── index.ts
├── package.json (updated dependencies)
├── tsconfig.json (already configured)
└── components.json (already configured)
```

---

## Next Steps

1. Install missing Shadcn/UI components
2. Create TypeScript types
3. Create API client library
4. Create WebSocket client class
5. Create Zustand chat store
6. Create UI components
7. Integrate ChatWidget into main page
8. Test and refine

---

**Plan Complete** ✅
