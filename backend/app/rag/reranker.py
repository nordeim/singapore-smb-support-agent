"""Cross-encoder reranker using HuggingFace."""


import torch
from sentence_transformers import CrossEncoder


class BGEReranker:
    """Reranker using BAAI/bge-reranker-v2-m3 cross-encoder."""

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", top_n: int = 5):
        """Initialize BGE reranker."""
        self.model = CrossEncoder(model_name)
        self.top_n = top_n
        self.model.eval()

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = None,
    ) -> list[dict]:
        """Rerank documents using cross-encoder scoring."""
        if top_k is None:
            top_k = self.top_n

        if not documents:
            return []

        pairs = [[query, doc["text"]] for doc in documents]

        with torch.no_grad():
            scores = self.model.predict(pairs)

        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])

        ranked_documents = sorted(
            documents, key=lambda x: x["rerank_score"], reverse=True
        )

        return ranked_documents[:top_k]

    async def async_rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = None,
    ) -> list[dict]:
        """Async wrapper for reranking."""
        return self.rerank(query, documents, top_k)
