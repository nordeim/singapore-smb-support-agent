"""Query transformation using LangChain LLM."""

from typing import Optional
from langchain_openai import ChatOpenAI
from app.config import settings


class QueryTransformer:
    """Transform user queries using LLM-based techniques."""

    def __init__(self):
        """Initialize query transformer."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_PRIMARY,
            temperature=0.3,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

    async def rewrite_query(self, query: str) -> str:
        """Rewrite query for better retrieval."""
        prompt = f"""
Rewrite the following user query for better information retrieval.
Keep the original meaning but make it more specific and search-friendly.

Original query: {query}

Rewritten query:
"""
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def classify_intent(self, query: str) -> str:
        """Classify user intent."""
        prompt = f"""
Classify the user intent into one of these categories:
- information: The user is asking for general information
- pricing: The user is asking about prices or costs
- hours: The user is asking about business hours
- services: The user is asking about services offered
- order: The user is asking about an existing order
- returns: The user is asking about returns or refunds
- complaint: The user is lodging a complaint
- escalation: The user is asking for human support

Query: {query}

Intent:
"""
        response = await self.llm.ainvoke(prompt)
        return response.content.strip().lower()

    async def detect_language(self, query: str) -> str:
        """Detect language (English-only for MVP)."""
        prompt = f"""
Detect the language of the following query.
For MVP, only support: en (English).

Query: {query}

Language (en, zh, ms, ta):
"""
        response = await self.llm.ainvoke(prompt)
        detected = response.content.strip().lower()
        return detected if detected in ["en", "zh", "ms", "ta"] else "en"

    async def decompose_query(self, query: str) -> Optional[list[str]]:
        """Decompose complex queries into sub-queries."""
        intent = await self.classify_intent(query)

        if intent in ["information", "services"]:
            prompt = f"""
Decompose the following query into 2-3 related sub-queries.
Each sub-query should be self-contained and searchable.

Original query: {query}

Sub-queries (list each on a new line):
"""
            response = await self.llm.ainvoke(prompt)
            sub_queries = [
                line.strip()
                for line in response.content.strip().split("\n")
                if line.strip()
            ]
            return sub_queries if sub_queries else None
        return None

    async def transform(self, query: str) -> dict:
        """Full query transformation pipeline."""
        rewritten = await self.rewrite_query(query)
        intent = await self.classify_intent(query)
        language = await self.detect_language(query)
        sub_queries = await self.decompose_query(query)

        return {
            "original": query,
            "rewritten": rewritten,
            "intent": intent,
            "language": language,
            "sub_queries": sub_queries,
        }
