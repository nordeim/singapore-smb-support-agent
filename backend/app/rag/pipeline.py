"""Main RAG pipeline orchestrator."""

from typing import List, Optional
from app.rag.query_transform import QueryTransformer
from app.rag.retriever import HybridRetriever
from app.rag.reranker import BGEReranker
from app.rag.context_compress import ContextCompressor
from app.models.domain import MessageRole
from app.config import settings


class RAGPipeline:
    """RAG pipeline orchestrating query transform → retrieval → rerank → compress."""

    def __init__(self):
        """Initialize RAG pipeline components."""
        self.query_transformer = QueryTransformer()
        self.retriever = HybridRetriever()
        self.reranker = BGEReranker(top_n=settings.RERANK_TOP_N)
        self.compressor = ContextCompressor(token_budget=settings.CONTEXT_TOKEN_BUDGET)

    async def run(
        self,
        query: str,
        session_id: str,
        conversation_history: List[dict],
    ) -> dict:
        """Execute full RAG pipeline."""
        transform_result = await self.query_transformer.transform(query)
        transformed_query = transform_result["rewitten"]

        docs = await self.retriever.hybrid_search(transformed_query)
        reranked_docs = await self.reranker.async_rerank(transformed_query, docs)

        context_result = self.compressor.compress(
            [doc["text"] for doc in reranked_docs],
            query,
        )

        return {
            "query": query,
            "transformed_query": transformed_query,
            "intent": transform_result["intent"],
            "language": transform_result["language"],
            "retrieved_count": len(docs),
            "reranked_count": len(reranked_docs),
            "context": context_result["context"],
            "compressed": context_result["compressed"],
            "sources": [
                {
                    "text": doc["text"],
                    "score": doc["rerank_score"],
                }
                for doc in reranked_docs[:5]
            ],
            "tokens_used": context_result["tokens_used"],
            "token_budget": settings.CONTEXT_TOKEN_BUDGET,
        }

    async def retrieve_context(
        self,
        query: str,
        session_id: Optional[str] = None,
    ) -> str:
        """Simple retrieval for context without full pipeline."""
        docs = await self.reranker.async_rerank(
            query,
            await self.retriever.hybrid_search(query),
        )

        context = "\n\n".join([doc["text"] for doc in docs[:3]])
        return context


rag_pipeline = RAGPipeline()
