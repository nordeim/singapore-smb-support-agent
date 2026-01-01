"""Hybrid retrieval combining dense (semantic) and sparse (BM25) search with RRF fusion."""

from qdrant_client import models
from qdrant_client.http.models import Filter

from app.config import settings
from app.ingestion.embedders.embedding import embedding_generator
from app.rag.qdrant_client import QdrantManager


class DenseRetriever:
    """Dense retrieval using semantic vector search with Qdrant."""

    def __init__(self):
        """Initialize hybrid retriever."""
        self.k = settings.RETRIEVAL_TOP_K

    async def dense_search(
        self,
        query: str,
        collection_name: str = "knowledge_base",
        filters: dict | None = None,
    ) -> list[models.ScoredPoint]:
        """Execute dense search using semantic vectors."""
        query_vector = await embedding_generator.generate_single(query)

        qdrant_filter = Filter(
            must=[models.FieldCondition(key="language", match=models.MatchValue(value="en"))]
        )

        dense_results = await self._dense_search(query_vector, collection_name, qdrant_filter)

        return dense_results

    async def _dense_search(
        self,
        query_vector: list[float],
        collection_name: str,
        filter: Filter,
    ) -> list[models.ScoredPoint]:
        """Dense vector search using native Qdrant client."""
        client = QdrantManager.get_client()

        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=filter,
            limit=self.k,
        )

        return results.points
