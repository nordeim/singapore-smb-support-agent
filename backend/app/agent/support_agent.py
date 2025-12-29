"""Main Singapore SMB Support Agent using Pydantic AI."""

from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.agent.prompts.system import SYSTEM_PROMPT
from app.agent.validators import ResponseValidator, ValidationResult
from app.memory.manager import MemoryManager


class AgentContext(BaseModel):
    """Context for agent operations."""

    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[int] = Field(None, description="User ID")
    conversation_summary: str = Field(default="", description="Conversation summary")
    recent_messages: list[dict] = Field(
        default_factory=list, description="Recent messages"
    )
    business_hours_status: str = Field(..., description="Current business hours status")


class AgentResponse(BaseModel):
    """Agent response model."""

    message: str = Field(..., description="Response message")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    sources: list[dict] = Field(default_factory=list, description="Source citations")
    escalated: bool = Field(default=False, description="Whether escalated to human")
    requires_followup: bool = Field(
        default=False, description="Whether followup needed"
    )
    ticket_id: Optional[str] = Field(None, description="Support ticket ID if created")


class SupportAgent:
    """
    Singapore SMB Support Agent.

    Uses RAG pipeline for knowledge retrieval, memory for context,
    and Pydantic AI for tool orchestration.
    """

    def __init__(
        self,
        rag_pipeline=None,
        memory_manager: Optional[MemoryManager] = None,
        db: Optional[AsyncSession] = None,
    ):
        """
        Initialize the support agent.

        Args:
            rag_pipeline: RAG pipeline for knowledge retrieval
            memory_manager: Memory manager for session management
            db: Database session
        """
        self.rag_pipeline = rag_pipeline
        self.memory_manager = memory_manager
        self.db = db
        self.validator = ResponseValidator()

    def _get_system_prompt(self, context: AgentContext) -> str:
        """Get formatted system prompt with context."""
        return SYSTEM_PROMPT.format(
            business_hours=f"{settings.BUSINESS_HOURS_START} - {settings.BUSINESS_HOURS_END}",
            business_hours_status=context.business_hours_status,
        )

    async def _assemble_context(
        self, session_id: str, user_id: Optional[int] = None
    ) -> AgentContext:
        """Assemble agent context from memory."""
        if not self.memory_manager:
            return AgentContext(
                session_id=session_id,
                user_id=None,
                business_hours_status="unknown",
            )

        working_memory = await self.memory_manager.get_working_memory(session_id)

        from app.dependencies import BusinessContext

        business_context = BusinessContext()
        business_hours_status = (
            "open" if business_context.is_business_hours() else "closed"
        )

        return AgentContext(
            session_id=session_id,
            user_id=user_id,
            conversation_summary=working_memory.get("conversation_summary", ""),
            recent_messages=working_memory.get("recent_messages", []),
            business_hours_status=business_hours_status,
        )

        working_memory = await self.memory_manager.get_working_memory(session_id)

        from app.dependencies import BusinessContext

        business_context = BusinessContext()
        business_hours_status = (
            "open" if business_context.is_business_hours() else "closed"
        )

        return AgentContext(
            session_id=session_id,
            user_id=user_id,
            conversation_summary=working_memory.get("conversation_summary", ""),
            recent_messages=working_memory.get("recent_messages", []),
            business_hours_status=business_hours_status,
        )

    async def process_message(
        self,
        message: str,
        session_id: str,
        user_id: Optional[int] = None,
    ) -> AgentResponse:
        """
        Process a user message and generate a response.

        Args:
            message: User message
            session_id: Session identifier
            user_id: User ID (optional)

        Returns:
            AgentResponse with generated response
        """
        try:
            context = await self._assemble_context(session_id, user_id)

            validation_result = self.validator.validate_response(
                text=message,
                context={"session_id": session_id, "user_id": user_id},
            )

            if validation_result.requires_escalation:
                return await self._escalate_message(
                    message=message,
                    reason=f"Customer sentiment: {validation_result.sentiment.value}",
                    session_id=session_id,
                    user_id=user_id,
                )

            knowledge_result = None
            sources = []

            if self.rag_pipeline:
                from app.agent.tools.retrieve_knowledge import retrieve_knowledge
                from app.config import settings

                knowledge_result = await retrieve_knowledge(
                    query=message,
                    session_id=session_id,
                    rag_pipeline=self.rag_pipeline,
                )

                if knowledge_result.success:
                    sources = knowledge_result.sources

            response_text = self._generate_response(
                query=message,
                knowledge=knowledge_result.knowledge if knowledge_result else "",
                context=context,
            )

            conversation_id = None
            if self.memory_manager and user_id:
                conversation = await self.memory_manager.get_or_create_conversation(
                    session_id=session_id,
                    user_id=user_id,
                )
                conversation_id = conversation.get("id")

                if conversation_id:
                    await self.memory_manager.save_message_with_metadata(
                        conversation_id=conversation_id,
                        role="user",
                        content=message,
                    )
                    await self.memory_manager.save_message_with_metadata(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=response_text,
                        confidence=knowledge_result.confidence
                        if knowledge_result
                        else 0.7,
                    )

            confidence = knowledge_result.confidence if knowledge_result else 0.7

            validation_result = self.validator.validate_response(
                text=response_text,
                confidence=confidence,
            )

            if validation_result.requires_escalation:
                return await self._escalate_message(
                    message=message,
                    reason="Low confidence or compliance issue",
                    session_id=session_id,
                    user_id=user_id,
                )

            return AgentResponse(
                message=response_text,
                confidence=confidence,
                sources=sources,
                requires_followup=validation_result.requires_followup,
                ticket_id=None,
            )

        except Exception as e:
            return AgentResponse(
                message="I apologize, but I'm experiencing a technical issue. Let me connect you with a human agent.",
                confidence=0.0,
                sources=[],
                ticket_id=None,
            )

    def _generate_response(
        self,
        query: str,
        knowledge: str,
        context: AgentContext,
    ) -> str:
        """Generate response using system prompt and knowledge."""
        if knowledge:
            return f"""Based on our knowledge base, here's what I can help you with:

{knowledge}

Is there anything else you'd like to know?"""
        else:
            return """I couldn't find specific information about your inquiry in my knowledge base. 

Could you provide more details or would you like me to connect you with a human agent who can assist you better?"""

    async def _escalate_message(
        self,
        message: str,
        reason: str,
        session_id: str,
        user_id: Optional[int] = None,
    ) -> AgentResponse:
        """Escalate message to human support."""
        from app.agent.tools.escalate_to_human import escalate_to_human

        escalation_result = await escalate_to_human(
            reason=f"{reason}. Original query: {message}",
            urgency="normal",
            session_id=session_id,
            user_id=user_id,
            db=self.db,
        )

        ticket_id = None
        if escalation_result.ticket:
            ticket_id = escalation_result.ticket.ticket_id

        return AgentResponse(
            message=escalation_result.message,
            confidence=1.0,
            sources=[],
            escalated=True,
            ticket_id=ticket_id,
        )


async def get_support_agent(
    rag_pipeline=None,
    memory_manager: Optional[MemoryManager] = None,
    db: Optional[AsyncSession] = None,
) -> SupportAgent:
    """Factory function to create support agent instance."""
    return SupportAgent(
        rag_pipeline=rag_pipeline,
        memory_manager=memory_manager,
        db=db,
    )
