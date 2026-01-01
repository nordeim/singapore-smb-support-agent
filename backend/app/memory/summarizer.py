"""Conversation summarizer using LLM via OpenRouter."""

from langchain_openai import ChatOpenAI

from app.config import settings


class ConversationSummarizer:
    """Summarize conversations using LLM for context compression."""

    def __init__(self):
        """Initialize conversation summarizer."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_PRIMARY,
            temperature=0.3,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

    async def summarize_conversation(
        self,
        messages: list[dict],
    ) -> str:
        """Summarize conversation messages."""
        if len(messages) < 5:
            return None

        prompt = f"""
Summarize the following customer support conversation for context compression.
Keep key points, decisions, and action items.

Conversation:
{self._format_messages(messages)}

Summary (2-4 sentences max):
"""
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def summarize_old_messages(
        self,
        messages: list[dict],
        keep_last: int = 5,
    ) -> str:
        """Summarize older messages while keeping recent ones."""
        if len(messages) <= keep_last:
            return None

        old_messages = messages[:-keep_last]
        prompt = f"""
Summarize the following customer support messages.
These messages will be archived to save context space.

Messages:
{self._format_messages(old_messages)}

Summary (2-3 sentences max):
"""
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    def _format_messages(self, messages: list[dict]) -> str:
        """Format messages for prompt."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)


conversation_summarizer = ConversationSummarizer()
