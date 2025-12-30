"""Memory manager orchestrating short-term, long-term, and summarization."""

from typing import Optional

from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.memory.summarizer import ConversationSummarizer
from app.config import settings


class MemoryManager:
    """Memory manager orchestrating all memory layers."""

    SUMMARY_THRESHOLD = 20

    def __init__(self, db_session):
        """Initialize memory manager with database session."""
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(db_session)
        self.summarizer = ConversationSummarizer()

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session from short-term memory."""
        return await self.short_term.get_session(session_id)

    async def save_session(self, session_id: str, session_data: dict) -> None:
        """Save session to short-term memory."""
        await self.short_term.save_session(session_id, session_data)

    async def add_message_to_session(self, session_id: str, message: dict) -> None:
        """Add message to short-term memory session."""
        await self.short_term.add_message(session_id, message)

    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """Get conversation history from short-term memory."""
        session_data = await self.get_session(session_id)
        if not session_data:
            return []

        messages = session_data.get("messages", [])
        return messages[offset : offset + limit]

    async def check_summary_threshold(self, session_id: str) -> bool:
        """Check if conversation needs summarization."""
        message_count = await self.short_term.increment_message_count(session_id)
        return message_count >= self.SUMMARY_THRESHOLD

    async def trigger_summarization(self, session_id: str, user_id: int) -> str:
        """Trigger conversation summarization when threshold reached."""
        messages = await self.get_conversation_history(session_id, limit=self.SUMMARY_THRESHOLD)

        if not messages:
            return "No messages to summarize"

        summary = await self.summarizer.summarize_conversation(messages)

        conversation = await self.long_term.get_conversation_by_session_id(session_id)
        if not conversation:
            return "Conversation not found"

        await self.long_term.save_conversation_summary(
            conversation.id,
            summary,
            message_range_start=0,
            message_range_end=len(messages),
        )

        return summary

    async def get_or_create_conversation(
        self,
        session_id: str,
        user_id: int,
    ) -> dict:
        """Get or create conversation from long-term memory."""
        conversation = await self.long_term.get_conversation_by_session_id(session_id)

        if not conversation:
            conversation = await self.long_term.create_conversation(user_id, session_id)

        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "session_id": conversation.session_id,
            "language": conversation.language,
            "summary_count": conversation.summary_count,
        }

    async def save_message_with_metadata(
        self,
        session_id: str,
        conversation_id: int,
        role: str,
        content: str,
        confidence: Optional[float] = None,
        sources: Optional[str] = None,
    ) -> dict:
        """Save message to both short-term and long-term memory."""
        from datetime import datetime

        message_data = {
            "role": role,
            "content": content,
            "confidence": confidence,
            "sources": sources,
            "created_at": datetime.utcnow(),
        }

        await self.add_message_to_session(session_id, message_data)

        await self.long_term.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            confidence=confidence,
            sources=sources,
        )

        return message_data

    async def get_working_memory(
        self,
        session_id: str,
        max_tokens: int = 4000,
    ) -> dict:
        """Assemble working memory for LLM context."""
        session = await self.get_session(session_id)
        if not session:
            return {
                "system": "",
                "conversation_summary": "",
                "recent_messages": [],
                "tokens_available": max_tokens,
            }

        recent_messages = await self.get_conversation_history(session_id, limit=5)
        conversation = await self.long_term.get_conversation_by_session_id(session_id)

        summaries = []
        if conversation:
            summaries = await self.long_term.get_conversation_summaries(conversation.id)

        context = {
            "system": "You are a Singapore SMB customer support specialist.",
            "conversation_summary": self._get_latest_summary(summaries),
            "recent_messages": recent_messages,
            "tokens_available": max_tokens - len(str(recent_messages)) * 50,
        }

        return context

    def _get_latest_summary(self, summaries: list) -> str:
        """Get most recent conversation summary."""
        if not summaries:
            return ""

        return summaries[0].summary


def get_memory_manager(db_session) -> MemoryManager:
    """Factory function to create memory manager instance."""
    return MemoryManager(db_session)
