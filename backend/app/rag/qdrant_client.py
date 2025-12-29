"""Qdrant client initialization and collection setup."""

from typing import Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, Filter
from app.config import settings


class QdrantManager:
    """Qdrant client manager."""

    _instance: Optional[QdrantClient] = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        """Get or create Qdrant client instance."""
        if cls._instance is None:
            cls._instance = QdrantClient(url=settings.QDRANT_URL)
        return cls._instance

    @classmethod
    async def initialize_collections(cls) -> None:
        """Initialize Qdrant collections for knowledge base and summaries."""
        client = cls.get_client()

        collections = client.get_collections()

        existing_collections = {c.name for c in collections.collections} if collections else set()

        if "knowledge_base" not in existing_collections:
            client.create_collection(
                collection_name="knowledge_base",
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )

        if "conversation_summaries" not in existing_collections:
            client.create_collection(
                collection_name="conversation_summaries",
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )

    @classmethod
    async def upsert_documents(cls, collection_name: str, points: list[models.PointStruct]) -> None:
        """Upsert documents to Qdrant collection."""
        client = cls.get_client()
        client.upsert(collection_name=collection_name, points=points)

    @classmethod
    async def search(
        cls,
        collection_name: str,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> list[models.ScoredPoint]:
        """Search documents in Qdrant collection."""
        client = cls.get_client()
        search_filter = Filter(
            must=[models.FieldCondition(key="language", match=models.MatchValue(value="en"))]
        )

        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=search_filter,
            limit=limit,
            score_threshold=score_threshold,
        )

        return results.points


qdrant_client = QdrantManager.get_client()
