"""Chat API routes with WebSocket support for Singapore SMB Support Agent."""


from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.support_agent import get_support_agent
from app.dependencies import get_db, get_memory_manager
from app.models.schemas import ChatRequest, ChatResponse, SourceCitation

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer(auto_error=False)


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(
        self,
        session_id: str,
        message: dict,
    ):
        """Send a message to a specific session."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()


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
    try:
        session_data = await memory_manager.get_session(request.session_id)

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found. Please start a new session.",
            )

        user_id = session_data.get("user_id")

        agent = await get_support_agent(
            rag_pipeline=None,
            memory_manager=memory_manager,
            db=db,
        )

        response = await agent.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=user_id,
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}",
        )


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection
        db: Database session
    """
    session_id = None

    try:
        session_id = websocket.query_params.get("session_id")
        if not session_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        memory_manager = await get_memory_manager(db)

        session_data = await memory_manager.get_session(session_id)
        if not session_data:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "Session not found. Please start a new session.",
                }
            )
            await websocket.close()
            return

        await manager.connect(session_id, websocket)

        agent = await get_support_agent(
            rag_pipeline=None,
            memory_manager=memory_manager,
            db=db,
            ws_manager=manager,
        )

        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to support agent",
                "session_id": session_id,
            }
        )

        while True:
            data = await websocket.receive_json()

            message_type = data.get("type", "message")
            message_content = data.get("message", "")

            if message_type == "message":
                if not message_content:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Message cannot be empty",
                        }
                    )
                    continue

                user_id = session_data.get("user_id")

                response = await agent.process_message(
                    message=message_content,
                    session_id=session_id,
                    user_id=user_id,
                )

                await websocket.send_json(
                    {
                        "type": "response",
                        "session_id": session_id,
                        "message": response.message,
                        "confidence": response.confidence,
                        "sources": response.sources,
                        "requires_followup": response.requires_followup,
                        "escalated": response.escalated,
                        "ticket_id": response.ticket_id,
                    }
                )

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif message_type == "disconnect":
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        if session_id and session_id in manager.active_connections:
            await manager.active_connections[session_id].send_json(
                {
                    "type": "error",
                    "message": f"Error: {str(e)}",
                }
            )
    finally:
        if session_id:
            manager.disconnect(session_id)


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    memory_manager=Depends(get_memory_manager),
    token: str | None = Depends(security),
):
    """
    Get session information.

    Args:
        session_id: Session identifier
        memory_manager: Memory manager instance
        token: Optional authentication token

    Returns:
        Session data
    """
    try:
        session_data = await memory_manager.get_session(session_id)

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        return {
            "session_id": session_id,
            "messages": session_data.get("messages", []),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session: {str(e)}",
        )
