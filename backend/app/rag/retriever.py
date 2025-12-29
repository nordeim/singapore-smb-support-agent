"""Hybrid retrieval combining dense (semantic) and sparse (BM25) search with RRF fusion."""

from typing import List, Optional
from qdrant_client import models
from qdrant_client.http.models import Distance, Filter, PointStruct
from langchain_qdrant import FastEmbedSparse, RetrievalMode
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from app.ingestion.embedders.embedding import embedding_generator
from app.config import settings


class HybridRetriever:
    """Hybrid retrieval combining dense and sparse search with RRF fusion."""

    def __init__(self):
        """Initialize hybrid retriever."""
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base=settings.OPENROUTER_BASE_URL,
        )
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.k = settings.RETRIEVAL_TOP_K

    async def hybrid_search(
        self,
        query: str,
        collection_name: str = "knowledge_base",
        filters: Optional[dict] = None,
    ) -> List[models.ScoredPoint]:
        """Execute hybrid search combining dense and sparse results with RRF fusion."""
        query_vector = await embedding_generator.generate_single(query)

        qdrant_filter = Filter(
            must=[
                models.FieldCondition(
                    key="language", match=models.MatchValue(value="en")
                )
            ]
        )

        dense_results = await self._dense_search(
            query_vector, collection_name, qdrant_filter
        )

        sparse_results = await self._sparse_search(
            query, collection_name, qdrant_filter
        )

        fused_results = self._reciprocal_rank_fusion(dense_results, sparse_results)
        return fused_results

    async def _dense_search(
        self,
        query_vector: List[float],
        collection_name: str,
        filter: Filter,
    ) -> List[models.ScoredPoint]:
        """Dense vector search using Qdrant."""
        client = Qdrant.from_existing_collection(
            embedding=self.embeddings,
            collection_name=collection_name,
            url=settings.QDRANT_URL,
        )

        results = await client.asimilarity_search_with_score(
            query_vector,
            k=self.k,
            filter=filter,
        )

        return results

    async def _sparse_search(
        self, query: str, collection_name: str, filter: Filter
    ) -> List[models.ScoredPoint]:
        """Sparse BM25 search using Qdrant FastEmbedSparse."""
        client = Qdrant.from_existing_collection(
            sparse_embedding=self.sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            collection_name=collection_name,
            url=settings.QDRANT_URL,
        )

        results = await client.asimilarity_search_with_score(
            query,
            k=self.k,
            filter=filter,
        )

        return results

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[models.ScoredPoint],
        sparse_results: List[models.ScoredPoint],
        k: int = 60,
    ) -> List[models.ScoredPoint]:
        """Reciprocal Rank Fusion (RRF) to combine search results."""
        score_dict = {}

        for i, result in enumerate(dense_results):
            point_id = result.id
            if point_id not in score_dict:
                score_dict[point_id] = 0
            score_dict[point_id] += 1.0 / (k + i + 1)

        for i, result in enumerate(sparse_results):
            point_id = result.id
            if point_id not in score_dict:
                score_dict[point_id] = 0
            score_dict[point_id] += 1.0 / (k + i + 1)

        unique_results = {
            result.id: result for result in dense_results + sparse_results
        }

        sorted_results = sorted(
            unique_results.values(),
            key=lambda x: score_dict[x.id],
            reverse=True,
        )

        return sorted_results[: self.k]
