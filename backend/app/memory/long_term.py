"""Long-term memory using PostgreSQL with SQLAlchemy async."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    Conversation,
    ConversationSummary,
    Message,
    SupportTicket,
    User,
)


class LongTermMemory:
    """Long-term memory using PostgreSQL for persistent storage."""

    def __init__(self, db: AsyncSession):
        """Initialize long-term memory with database session."""
        self.db = db

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        consent_given_at: datetime,
        consent_version: str = "v1.0",
        data_retention_days: int = 30,
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            consent_given_at=consent_given_at,
            consent_version=consent_version,
            data_retention_days=data_retention_days,
            is_active=True,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .where(User.is_active)
            .where(not User.is_deleted)
        )
        return result.scalar_one_or_none()

    async def create_conversation(
        self,
        user_id: int,
        session_id: str,
        language: str = "en",
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            language=language,
            is_active=True,
            summary_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation_by_session_id(self, session_id: str) -> Conversation | None:
        """Get conversation by session ID."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .where(Conversation.is_active)
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        confidence: float | None = None,
        sources: str | None = None,
    ) -> Message:
        """Add a message to conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            confidence=confidence,
            sources=sources,
            created_at=datetime.utcnow(),
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_conversation_messages(
        self,
        conversation_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Message]:
        """Get messages for a conversation with pagination."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def save_conversation_summary(
        self,
        conversation_id: int,
        summary: str,
        message_range_start: int,
        message_range_end: int,
        embedding_vector: str | None = None,
        metadata: str | None = None,
    ) -> ConversationSummary:
        """Save conversation summary."""
        conv_summary = ConversationSummary(
            conversation_id=conversation_id,
            summary=summary,
            message_range_start=message_range_start,
            message_range_end=message_range_end,
            embedding_vector=embedding_vector,
            metadata=metadata,
            created_at=datetime.utcnow(),
        )
        self.db.add(conv_summary)

        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.summary_count += 1
            conversation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(conv_summary)
        return conv_summary

    async def get_conversation_summaries(
        self,
        conversation_id: int,
    ) -> list[ConversationSummary]:
        """Get all summaries for a conversation."""
        result = await self.db.execute(
            select(ConversationSummary)
            .where(ConversationSummary.conversation_id == conversation_id)
            .order_by(ConversationSummary.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_support_ticket(
        self,
        conversation_id: int,
        reason: str,
        status: str = "open",
    ) -> SupportTicket:
        """Create a support ticket for human escalation."""
        ticket = SupportTicket(
            conversation_id=conversation_id,
            reason=reason,
            status=status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def update_ticket_status(
        self,
        ticket_id: int,
        status: str,
        assigned_to: str | None = None,
    ) -> SupportTicket | None:
        """Update ticket status."""
        result = await self.db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if ticket:
            ticket.status = status
            ticket.assigned_to = assigned_to
            ticket.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(ticket)
        return ticket

    async def expire_user_data(self, user_id: int) -> None:
        """Mark user data for PDPA-compliant expiry (soft delete)."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
        await self.db.commit()

    async def get_conversation_count(self, user_id: int) -> int:
        """Get total conversation count for a user."""
        result = await self.db.execute(
            select(func.count(Conversation.id))
            .where(Conversation.user_id == user_id)
            .where(Conversation.is_active)
        )
        count = result.scalar()
        return count if count is not None else 0
