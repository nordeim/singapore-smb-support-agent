"""Test API route for OpenRouter LLM connectivity.

This test version focuses on verifying:
1. OpenRouter API key connectivity
2. LLM model instantiation
3. Agent response generation with knowledge retrieval
4. REST endpoint functionality

WebSocket and ConnectionManager commented out for this test.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.agent.support_agent import get_support_agent, AgentContext
from app.dependencies import get_db, get_memory_manager
from app.models.schemas import ChatRequest, ChatResponse, SourceCitation
from app.rag.pipeline import rag_pipeline
from app.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer(auto_error=False)

# ConnectionManager class COMMENTED OUT - Not needed for LLM connectivity test
# class ConnectionManager:
#     """Manage WebSocket connections."""
#     def __init__(self):
#         self.active_connections: dict[str, WebSocket] = {}
#
#     async def connect(self, session_id: str, websocket: WebSocket):
#         """Accept a WebSocket connection."""
#         await websocket.accept()
#         self.active_connections[session_id] = websocket
#
#     def disconnect(self, session_id: str):
#         """Remove a WebSocket connection."""
#         if session_id in self.active_connections:
#             del self.active_connections[session_id]
#
#     async def send_message(
#         self,
#         session_id: str,
#         message: dict,
#     ):
#         """Send a message to a specific session."""
#         if session_id in self.active_connections:
#             await self.active_connections[session_id].send_json(message)
#
# manager = ConnectionManager()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    memory_manager=Depends(get_memory_manager),
    token: str | None = Depends(security),
):
    """
    Process a chat message using the support agent.

    Args:
        request: Chat request with message and session_id
        db: Database session
        memory_manager: Memory manager instance
        token: Optional authentication token

    Returns:
        ChatResponse with agent response
    """
    print(f"\n{'=' * 50}")
    print(f"LLM Connectivity Test - {datetime.now().isoformat()}")
    print(f"{'=' * 50}")

    # Log environment configuration
    print(f"\n[ENVIRONMENT CHECK]")
    print(
        f"OpenRouter API Key: {settings.OPENROUTER_API_KEY[:20]}...{settings.OPENROUTER_API_KEY[-4:]}"
    )
    print(f"OpenRouter Base URL: {settings.OPENROUTER_BASE_URL}")
    print(f"LLM Model Primary: {settings.LLM_MODEL_PRIMARY}")
    print(f"LLM Temperature: {settings.LLM_TEMPERATURE}")
    print(f"\n{'=' * 50}")

    try:
        session_data = await memory_manager.get_session(request.session_id)

        if not session_data:
            # Create test session if it doesn't exist
            print(f"[SESSION] Session '{request.session_id}' not found, creating test session...")
            await memory_manager.create_session(
                session_id=request.session_id,
                user_id=999,  # Test user ID
            )
            session_data = await memory_manager.get_session(request.session_id)
            print(f"[SESSION] Test session created successfully")
        else:
            print(f"[SESSION] Using existing session '{request.session_id}'")

        user_id = session_data.get("user_id", 999)

        print(f"\n[RAG PIPELINE CHECK]")
        print(f"RAG Pipeline Type: {type(rag_pipeline).__name__}")
        print(f"RAG Pipeline Methods: {[m for m in dir(rag_pipeline) if not m.startswith('_')]}")
        print(f"Has run method: {hasattr(rag_pipeline, 'run')}")
        print(f"Has retrieve_context method: {hasattr(rag_pipeline, 'retrieve_context')}")

        print(f"\n{'=' * 50}")
        print(f"[AGENT INITIALIZATION]")
        print(f"{'=' * 50}")

        agent = await get_support_agent(
            rag_pipeline=rag_pipeline,
            memory_manager=memory_manager,
            db=db,
        )

        print(f"✓ Support Agent initialized")
        print(f"✓ Agent has RAG pipeline: {agent.rag_pipeline is not None}")
        print(f"✓ Agent has memory manager: {agent.memory_manager is not None}")
        print(f"✓ Agent has DB session: {agent.db is not None}")
        print(f"{'=' * 50}")

        print(f"\n[TESTING KNOWLEDGE RETRIEVAL]")
        print(f"Test Query: '{request.message}'")
        print(f"{'=' * 50}")

        response = await agent.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=user_id,
        )

        print(f"\n[RESPONSE GENERATED]")
        print(f"{'=' * 50}")
        print(f"Response Length: {len(response.message)} characters")
        print(f"Response Confidence: {response.confidence}")
        print(f"Sources Retrieved: {len(response.sources)}")
        print(f"Sources List: {response.sources}")
        print(f"Requires Follow-up: {response.requires_followup}")
        print(f"Escalated: {response.escalated}")
        print(f"Ticket ID: {response.ticket_id}")
        print(f"{'=' * 50}")

        # Check if response contains knowledge
        if response.sources:
            print(f"[✓] KNOWLEDGE RETRIEVED SUCCESSFULLY")
            for i, source in enumerate(response.sources[:3], 1):
                print(f"  Source {i}: {source.get('content', '')[:100]}...")
                print(f"    Score: {source.get('score', 0.0)}")
        else:
            print(f"[⚠️] NO KNOWLEDGE RETRIEVED - Response from LLM only")

        print(f"\n{'=' * 50}")
        print(f"[FINAL RESPONSE]")
        print(f"{'=' * 50}")
        print(f"Message Preview (first 200 chars):")
        print(response.message[:200])
        if len(response.message) > 200:
            print(f"    ... ({len(response.message) - 200} more characters)")
        print(f"{'=' * 50}")

        source_citations = [
            SourceCitation(
                content=source.get("content", ""),
                metadata=source.get("metadata", {}),
                score=source.get("score", 0.0),
            )
            for source in response.sources
        ]

        return ChatResponse(
            session_id=request.session_id,
            message=response.message,
            confidence=response.confidence,
            sources=source_citations,
            requires_followup=response.requires_followup,
            escalated=response.escalated,
            ticket_id=response.ticket_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"\n[ERROR]")
        print(f"{'=' * 50}")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {str(e)}")
        print(f"{'=' * 50}")

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM connectivity test failed: {str(e)}",
        )


# WebSocket endpoint COMMENTED OUT - Not needed for LLM connectivity test
# @router.websocket("/ws")
# async def websocket_chat(
#     websocket: WebSocket,
#     db: AsyncSession = Depends(get_db),
# ):
#     """WebSocket endpoint COMMENTED OUT for LLM connectivity test."""
#     pass


if __name__ == "__main__":
    import uvicorn
    from app.main import app

    # Include test router
    app.include_router(router, prefix="/api/v1")

    print(f"\n{'=' * 60}")
    print(f"[STARTING TEST SERVER]")
    print(f"Router: Test Chat (LLM Connectivity)")
    print(f"URL: http://localhost:8001")
    print(f"Test this endpoint: http://localhost:8001/api/v1/chat")
    print(f"{'=' * 60}")
    print(f"\n[TEST COMMAND]")
    print(f"curl -X POST http://localhost:8001/api/v1/chat \\")
    print(f'  -H "Content-Type: application/json" \\')
    print(
        f'  -d \'{{"message": "Hello, can you tell me about your services?", "session_id": "test-llm-123"}}\''
    )
    print(f"{'=' * 60}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
    )
