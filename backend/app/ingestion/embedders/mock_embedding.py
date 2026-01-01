"""Mock embedding generator for testing without API costs."""

import random

from app.config import settings


class MockEmbeddingGenerator:
    """Generate mock embeddings for testing purposes."""

    def __init__(self):
        """Initialize mock embedding generator."""
        self.dimension = settings.EMBEDDING_DIMENSION

    async def generate(self, texts: list[str]) -> list[list[float]]:
        """Generate mock embeddings for a list of texts."""
        return [self._generate_single_vector(text) for text in texts]

    async def generate_single(self, text: str) -> list[float]:
        """Generate mock embedding for a single text."""
        return self._generate_single_vector(text)

    def _generate_single_vector(self, text: str) -> list[float]:
        """Generate a deterministic pseudo-random vector based on text content."""
        random.seed(hash(text))
        vector = [random.uniform(-1, 1) for _ in range(self.dimension)]

        # Normalize vector
        magnitude = sum(v * v for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector


def get_embedding_generator():
    """Factory function to create embedding generator instance."""
    return MockEmbeddingGenerator()
