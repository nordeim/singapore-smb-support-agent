"""Embedding generation for vector storage."""

from typing import List
from openai import AsyncOpenAI
from app.config import settings


class EmbeddingGenerator:
    """Generate embeddings using OpenAI via OpenRouter."""

    def __init__(self):
        """Initialize embedding generator."""
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    async def generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        return [item.embedding for item in response.data]

    async def generate_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        result = await self.generate([text])
        return result[0]


embedding_generator = EmbeddingGenerator()
