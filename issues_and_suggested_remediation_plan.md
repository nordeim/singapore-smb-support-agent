# Remediation Plan: Critical Issues
Priority 1: Fix RAG Retrieval Vector Type Mismatch
Location: backend/app/rag/retriever.py
Current Code (Line 46):
results = await client.asimilarity_search_with_score(
    query_vector,  # <--- ERROR: List[float] passed
    k=self.k,
    filter=filter,
)
Issue: LangChain's asimilarity_search_with_score expects a query: str parameter, but we're passing query_vector: List[float].
Impact: 
- Semantic search will crash
- All retrievals will yield zero results
- Users will get "I don't understand your question" responses
Root Cause: RAG pipeline expects dense embeddings from OpenAIEmbeddings class, but we're using MockEmbeddingGenerator which returns Listfloat.
Fix Options
Option A: Fix Retrieval to Use Correct Method
# Change from:
results = await client.asimilarity_search_with_score(query_vector, ...)
# To:
results = await client.asimilarity_search_by_vector(query_vector, ...)
Pros:
- Uses correct vector type (Listfloat)
- Semantic search works correctly
- Compatible with both real and mock embeddings
Cons:
- Requires backend change
- More complex than Option B
Option B: Fix Mock Embedding Generator to Return Correct Type
File: backend/app/ingestion/embedders/mock_embedding.py
Current Code:
async def generate(self, texts: List[str]) -> List[List[float]]:
    return [self._generate_single_vector(text) for text in texts]
def _generate_single_vector(self, text: str) -> List[float]:
    import random
    random.seed(hash(text))
    vector = [random.uniform(-1, 1) for _ in range(self.dimension)]
    
    # Normalize vector
    magnitude = sum(v * v for v in vector)
    if magnitude > 0:
        vector = [v / magnitude for v in vector]
    
    return vector
Issue: Returns List[float] but should return a flat list for query_vector parameter.
Fix:
async def generate_single(self, text: str) -> List[float]:
    import random
    random.seed(hash(text))
    vector = [random.uniform(-1, 1) for _ in range(self.dimension)]
    return vector  # Return flat list, not nested list
Pros:
- Correct type for similarity search
- No backend changes required
- Minimal fix
Option C: Use String Query Type (RECOMMENDED)
File: backend/app/rag/retriever.py
Change both methods:
# Change from:
async def hybrid_search(self, query: str, ...) -> list[dict]:
# To:
async def hybrid_search(self, query: str, ...) -> list[dict]:
    from typing import cast
    # First try semantic search with string query
    try:
        semantic_results = await self.semantic_search(query)
        if semantic_results:
            return semantic_results
    except Exception as e:
        # Log and fall back
        import logging
        logging.warning(f"Semantic search failed: {e}, falling back to mock")
        semantic_results = []
    
    # Then try sparse search
    sparse_results = await self.sparse_search(query)
    
    # Combine with RRF (Reciprocal Rank Fusion)
    # ...
Pros:
- Uses string query type (correct)
- Still uses mock embeddings (works correctly)
- Simple fallback if semantic fails
- No code changes to retriever
Cons:
- Still returns mock results (no real search)
- Semantic search won't work with mock embeddings anyway
---
Priority 2: Wire WebSocket Client into ChatStore
Location: frontend/src/stores/chatStore.ts
Current State: 
- Has isThinking, setThinking actions
- Has expandedCitation state
- BUT: No WebSocket client integration
Issue: 
- Frontend sends messages via REST API (chatService.sendMessage)
- Thinking state is manually toggled in store
- No real-time streaming of agent thoughts
Root Cause: 
1. Backend WebSocket at /ws endpoint exists but never wired to frontend
2. chatStore.sendMessage uses REST API, not WebSocket
3. Thinking states are simulated (frontend heuristic), not real
Impact: 
- No streaming of real agent thoughts
- Frontend relies entirely on heuristic simulation
- Poor UX - user can't see true AI reasoning
Fix Plan
Step 1: Check Backend WebSocket Implementation
File: backend/app/api/routes/chat.py
Check: Does backend actually emit thought events via WebSocket?
# Look for WebSocket message emissions
# Should emit:
# - type: "thought"
# - step: str  # "retrieving", "formatting", "generating", etc.
Step 2A: If Backend Emits Thoughts
Files to Create/Modify:
1. backend/app/agent/support_agent.py - Add thought event emissions
2. backend/api/routes/chat.py - Wire thought events into WebSocket
Implementation in support_agent.py:
# Add to process_message method:
async def process_message(
    self,
    message: str,
    session_id: str,
    user_id: Optional[int] = None,
) -> AgentResponse:
    # ... existing code ...
    # After context assembly:
    context = await self._assemble_context(session_id, user_id)
    # NEW: Emit thought events
    await manager.send_message(
        session_id=session_id,
        type="thought",
        step="context_assembled"
    )
    # NEW: Start retrieval
    await manager.send_message(
        session_id=session_id,
        type="thought",
        step="retrieving"
    )
    # Check if retrieval is configured
    knowledge_result = None
    if self.rag_pipeline:
        # ... existing code ...
        # Emit completion
        await manager.send_message(
            session_id=session_id,
            type="thought",
            step="retrieval_complete"
        )
    # NEW: Start generation
    if knowledge_result:
        await manager.send_message(
            session_id=session_id=session_id,
            type="thought",
            step="generating_response"
        )
    # ... rest of method ...
Implementation in chat.py (WebSocket handler):
# Update websocket_chat function to handle thought events
async def websocket_chat(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    session_id = websocket.query_params.get("session_id")
    
    # ... existing code ...
    # NEW: Add thought event handling
    while True:
        data = await websocket.receive_json()
        
        # Existing message handling
        message_type = data.get("type", "message")
        
        # NEW: Handle thought events
        thought_step = data.get("step")
        thought_details = data.get("details")
        
        if message_type == "thought":
            await websocket.send_json({
                "type": "thought",
                "session_id": session_id,
                "step": thought_step,
                "details": thought_details,
            })
Step 2B: If Backend Does NOT Emit Thoughts
Files to Modify:
1. frontend/src/stores/chatStore.ts - Add thought event receiver
2. frontend/src/lib/websocket.ts - Add WebSocket client wrapper
New WebSocket Client (frontend/src/lib/websocket.ts):
'use client';
import { type WebSocketMessage } from '@/types';
export class WebSocketClient {
  private ws: WebSocket | null;
  private url: string;
  private reconnectAttempts = 0;
  constructor(url: string) {
    this.url = url;
    this.connect();
  }
  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => {
      console.log('[WebSocket] Connected');
      this.reconnectAttempts = 0;
    this.ws.onerror = this.handleDisconnect;
      this.ws.onmessage = this.handleMessage;
    };
    this.ws.onclose = () => {
      this.handleDisconnect();
    };
  }
  private handleDisconnect() {
    this.reconnectAttempts++;
    console.log(`[WebSocket] Disconnected. Attempt ${this.reconnectAttempts}`);
    if (this.reconnectAttempts < 3) {
      setTimeout(() => this.connect(), 3000);
    }
  }
  private handleMessage(event: MessageEvent) {
    const data = JSON.parse(event.data);
    if (data.type === 'thought') {
      // Dispatch thought event to store
      const { useChatStore } = await import('@/stores/chatStore');
      useChatStore.getState().setThinking(true);
      
      // Auto-clear after 10 seconds
      setTimeout(() => {
        useChatStore.getState().setThinking(false);
      }, 10000);
    }
  }
  disconnect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.close();
    }
  }
  // Send message through WebSocket (if connected)
  sendMessage(message: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: "message",
        message: message,
      }));
    }
  }
}
export const wsClient = new WebSocketClient('ws://localhost:8000/ws');
Update ChatStore:
// Add to ChatStore interface:
interface ChatStore {
  // ... existing ...
  isThinking: boolean;
  onThoughtMessage: (message: WebSocketMessage) => void;  // NEW
}
// Add to actions:
onThoughtMessage: (message: WebSocketMessage) => void;
Update ChatWidget.tsx:
// Connect to WebSocket on mount
useEffect(() => {
  wsClient.connect();
}, []);
// Use WebSocket for messages instead of REST API
const { sendMessage } = useChatStore();
const handleSendMessage = async (content: string) => {
  if (!wsClient.isConnected()) {
    // Fallback to REST
    const { sendMessage: restSend } = await import('@/lib/api');
    await restSend({ session_id: sessionId, message: content });
  } else {
    wsClient.sendMessage(content);
  }
};
Pros:
- Real-time thought streaming from backend
- Accurate AI reasoning transparency
- Better UX - users see actual process
- Thinking states are real, not simulated
Cons:
- Requires backend changes
- Increases complexity (fallback logic needed)
- WebSocket disconnection handling
Step 2C: Hybrid Approach (RECOMMENDED SHORT-TERM)
Keep the current architecture for now. Enhance it minimally:
1. Enhance ThinkingState component:
   - Display real thought steps from WebSocket if available
   - Fall back to heuristic if WebSocket not connected
   - Show "(Real-time)" indicator when using WebSocket
2. Keep chatStore thinking state:
   - Use WebSocket events to set isThinking
   - Fallback to manual setThinking for non-WebSocket mode
3. Update WebSocket client:
   - Add reconnection logic
   - Add automatic reconnection
   - Use exponential backoff
---
Priority 3: Fix Database Connection String (Minor)
Location: backend/app/memory/short_term.py:18
Issue: References settings.REDIS_URL (typo)
Status: ✅ FIXED
Action: Already fixed via sed command in Phase 8.1
---
Priority 4: Test Critical Path End-to-End
Test Checklist
- [ ] Backend WebSocket emits thought events
- [ ] Frontend WebSocket client connects successfully
- [ ] Thought states display correctly
- [ ] RAG retrieval works with string query
- [ ] Mock embeddings produce functional results
- [ ] Session expiry countdown works
- [ ] Confidence rings display correctly
- [ ] Evidence sheets open correctly
Test Commands
# Backend logs
docker logs smb_support_backend
# Frontend status
curl http://localhost:3000/
# WebSocket connection
wscat ws://localhost:8000/ws
# Database connection
docker exec smb_support_postgres psql -U postgresql://agent_user:dev_password_only@postgres:5432/support_agent
---
Execution Order
Phase 1: RAG Vector Type Fix (HIGH)
- [ ] Fix backend/app/rag/retriever.py (Option A, B, or C)
- [ ] Test all search methods
- [ ] Verify semantic search works
Phase 2: WebSocket Integration (HIGH)
- [ ] Implement backend thought event emission
- [ ] Create frontend WebSocket client
- [ ] Integrate with chatStore
- [ ] Add fallback to REST API
Phase 3: End-to-End Testing (MEDIUM)
- [ ] Run test checklist above
- [ ] Verify all features work end-to-end
---
Success Criteria
All critical fixes implemented, then system is production-ready for:
- ✅ Accurate RAG retrieval with proper vector types
- ✅ Real-time AI transparency via WebSocket
- ✅ Complete frontend visualization
- ✅ PDPA compliance features
- ✅ Trust-centric UX throughout
</arg_value><arg_key>filePath</arg_key><arg_value>/home/project/ai-agent/CRITICAL_FIXES_PLAN.md</arg_value></tool_call>
▣  Build · glm-4.7-free · 1m 34s
please save the remediation plan
pete
Thinking: <tool_call>write<arg_key>content</arg_key><arg_value># Remediation Plan - Execution Phase
🔴 Critical Issues Identified
Based on meticulous review of Codebase_Review_Analysis_Report.md, TWO CRITICAL BLOCKERS prevent system from functioning:
1. RAG Retriever Type Mismatch (BLOCKING)
File: backend/app/rag/retriever.py:46
Issue: await client.asimilarity_search_with_score(query_vector, ...)
Impact: COMPLETE SYSTEM FAILURE - RAG retrieval will crash on every query
Fix:
# Change line 46 from:
results = await client.asimilarity_search_with_score(
    query_vector, # <--- ERROR: passing list[float]
    k=self.k,
    filter=filter,
)
# To:
from qdrant_client import QdrantManager
class HybridRetriever:
    def __init__(self):
        self.client = QdrantManager.get_client()
        self.k = settings.HYBRID_K
        self.filter = settings.RERANKER_FUSION_K
    async def hybrid_search(self, query: str) -> list:
        # Generate query vector using real embeddings (not mock)
        from app.rag.embedders.embedding import EmbeddingGenerator
        embedder = EmbeddingGenerator()
        query_vector = await embedder.generate_single(query)
        return await self.client.asimilarity_search_by_vector_id(
            vector=query_vector,
            query_filter=Filter(must=[models.Filter(
                key="language",
                match=models.MatchValue(value="en")
            ]),
            limit=10,
        )
---
2. Ghost WebSocket Client (BLOCKING)
Files: 
- frontend/src/stores/chatStore.ts 
- frontend/src/components/chat/ChatWidget.tsx
Issue: WebSocketClient class exists in lib/websocket.ts but NEVER INSTANTIATED
Impact: Frontend cannot receive real-time agent thinking events
Fix:
// frontend/src/stores/chatStore.ts
import { WebSocketClient } from '@/lib/websocket';
import { chatService } from '@/lib/api';
// Add to ChatStore interface:
export interface ChatStore {
  // ... existing fields ...
  // Add WebSocket:
  socketClient: WebSocketClient | null;
  connect: (url: string) => void;
  disconnect: () => void;
  // ... rest of interface
}
// Add to store initialization:
socketClient: new WebSocketClient({
  url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001',
  onMessage: (msg: WSResponse) => { ... },
  onThought: (msg: WSMessage) => { ... },
  onConnected: () => { ... },
  onError: (error: string) => void,
});
// Connect action:
connect: async () => {
  const { addMessage } = get();
  await socketClient.connect();
  socketClient.connect();
  await addMessage({
    type: 'connected',
    session_id: 'system-init',
    message: 'WebSocket connected',
    role: 'system',
    timestamp: new Date(),
  });
};
// Disconnect action:
disconnect: async () => {
  await socketClient.disconnect();
  await socketClient.disconnect();
  await addMessage({
    type: 'disconnected',
    session_id: 'system-init',
    message: 'Disconnected from WebSocket',
    role: 'system',
    timestamp: new Date(),
  });
};
// Update sendMessage to use WebSocket:
sendMessage: async (content: string) => Promise<void> => {
  const { addMessage } = get();
  const { sessionId } = get();
  if (!sessionId) {
    await addMessage({
      type: 'error',
      session_id: 'system-init',
      message: 'No session ID. Cannot send message.',
      role: 'system',
      timestamp: new Date(),
    });
    return;
  }
  await socketClient.send({
    type: 'message',
    session_id: sessionId,
    message: content,
  });
},
And update backend to emit WS events:
# backend/app/api/routes/chat.py (WebSocket handler)
async def websocket_chat(websocket: WebSocket, db: AsyncSession):
    try:
        await manager.connect(session_id, websocket)
        agent = await get_support_agent(...)
        # Emit connected event
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Connected to support agent",
        })
        while True:
            data = await websocket.receive_json()
            # Forward messages as WSResponse events
            if data.get("type") == "message":
                await agent.process_message(
                    message=data.get("message", ""),
                    session_id=session_id,
                    user_id=user_id,
                )
                )
                await websocket.send_json({
                    "type": "response",
                    "session_id": session_id:
                    "message": response.message,
                    "confidence": response.confidence,
                    "sources": response.sources,
                    "requires_followup": response.requires_followup,
                    "escalated": response.escalated,
                    "ticket_id": response.ticket_id,
                })
            elif data.get("type") == "thought":
                await websocket.send_json({
                    "type": "thought",
                    "session_id": session_id,
                    "step": data.get("step", ""),
                    "details": data.get("details", ""),
                })
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
---
## 🔧 Execution Order
### Phase 1: CRITICAL FIXES (1-2 hours)
- [ ] **1.1** Fix RAG Retriever type mismatch
- [ ] **1.2** Wire WebSocket client into frontend
- [ ] Test hybrid search with correct parameters
### Phase 2: VERIFY (30 minutes)
- [ ] Test RAG retrieval returns results
- [ ] Verify frontend receives WebSocket events
- [ ] Test thought stream cycles
### Phase 3: VALIDATE (1 hour)
- [ ] Test complete chat flow
- [ ] Monitor for any remaining errors
---
## 📋 Files to Modify
### Critical (Blockers)
1. `backend/app/rag/retriever.py` - Fix hybrid_search method
2. `frontend/src/stores/chatStore.ts` - Add WebSocket client
3. `frontend/src/components/chat/ChatWidget.tsx` - Use WebSocket instead of REST
4. `backend/app/api/routes/chat.py` - Emit thought events through WebSocket
### Supporting Changes
5. `backend/app/rag/pipeline.py` - Update to use correct retriever
6. `frontend/src/lib/api.ts` - Update sendMessage to use WebSocket
7. `frontend/src/lib/websocket.ts` - Instantiate WebSocketClient in store
8. Add `frontend/src/types/index.ts` - Add WS message types
---
## ⏁️ Estimated Timeline
- **Phase 1**: 1-2 hours
- **Phase 2**: 30 minutes
- **Phase 3**: 1 hour
**Total**: 2-3 hours to unblock system
---
## ✅ Success Criteria
### Phase 1: RAG Fix
- [ ] Hybrid search accepts query_vector (List[float])
- [ ] Returns search results without type errors
- [ ] Test retrieval with sample query
### Phase 2: WebSocket
- [ ] WebSocketClient instantiated in chatStore
- [ ] WebSocket connect() action implemented
- [ ] Backend emits WS events (connected, message, thought, ping)
- [ ] Frontend receives and processes WS events
- [ ] Real-time thought display works
### Phase 3: Full Integration
- [ ] End-to-end flow works:
  - [ ] User sends message via WebSocket
- [ ] Backend processes with RAG
  [ ] Thought events stream to frontend
  [ - ] Confidence and sources return correctly
---
## 🎯 Command List
```bash
# Phase 1.1 - Test current retriever (should fail):
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"test pricing"}'
# Phase 1.2 - Fix RAG retriever:
# Edit backend/app/rag/retriever.py line 46
Phase 2.1 - Start backend with fix:
cd backend && docker compose down && docker compose up -d
Phase 2.2 - Watch logs:
docker compose logs -f smb_support_backend
Verify WebSocket events work:
Open browser console
Watch for WS events in console
Send a test message
---
**Status**: READY TO EXECUTE
**Priority**: CRITICAL - System blocked by two errors
