"""Context compression for working memory management."""

from typing import List, Optional
from app.config import settings


class ContextCompressor:
    """Compress retrieved context within token budget."""

    def __init__(
        self,
        token_budget: int = settings.CONTEXT_TOKEN_BUDGET,
    ):
        """Initialize context compressor."""
        self.token_budget = token_budget

    def compress(
        self,
        documents: List[str],
        query: str = "",
    ) -> dict:
        """Compress documents within token budget using extractive compression."""
        total_tokens = self._estimate_tokens(documents + [query])

        if total_tokens <= self.token_budget:
            return {
                "context": "\n\n".join(documents),
                "compressed": False,
                "tokens_used": total_tokens,
                "tokens_budget": self.token_budget,
            }

        sorted_docs = self._sort_by_relevance(documents, query)
        compressed_docs = self._extractive_compression(
            sorted_docs, self.token_budget - len(query) // 4
        )

        return {
            "context": "\n\n".join(compressed_docs),
            "compressed": True,
            "tokens_used": len(query) // 4 + self._estimate_tokens(compressed_docs),
            "tokens_budget": self.token_budget,
        }

    def _estimate_tokens(self, texts: List[str]) -> int:
        """Estimate token count (rough approximation: 4 chars per token)."""
        total_chars = sum(len(text) for text in texts)
        return total_chars // 4

    def _sort_by_relevance(self, documents: List[str], query: str) -> List[str]:
        """Sort documents by relevance to query (keyword matching)."""
        if not query:
            return documents

        query_keywords = set(query.lower().split())

        scored = []
        for doc in documents:
            doc_lower = doc.lower()
            matches = sum(1 for keyword in query_keywords if keyword in doc_lower)
            scored.append((doc, matches))

        return [doc for doc, _ in sorted(scored, key=lambda x: x[1], reverse=True)]

    def _extractive_compression(
        self,
        documents: List[str],
        max_tokens: int,
    ) -> List[str]:
        """Extractive compression to keep most relevant content."""
        compressed = []
        current_tokens = 0

        for doc in documents:
            doc_tokens = self._estimate_tokens([doc])

            if current_tokens + doc_tokens > max_tokens:
                break

            key_sentences = self._extract_key_sentences(doc)
            compressed_doc = " ".join(key_sentences)
            compressed.append(compressed_doc)

            current_tokens += self._estimate_tokens([compressed_doc])

        return compressed

    def _extract_key_sentences(self, text: str, max_sentences: int = 3) -> List[str]:
        """Extract key sentences from document."""
        import re

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])", text) if s.strip()]

        if len(sentences) <= max_sentences:
            return sentences

        priority_keywords = [
            "therefore",
            "important",
            "note",
            "key",
            "main",
            "additionally",
            "however",
        ]

        scored = []
        for i, sentence in enumerate(sentences):
            score = 0
            sentence_lower = sentence.lower()
            for keyword in priority_keywords:
                if keyword in sentence_lower:
                    score += 1

            if "?" in sentence:
                score += 1

            if i < len(sentences) - 1:
                scored.append((sentence, score))

        scored.append((sentences[-1], 1))

        sorted_sentences = [
            s for s, _ in sorted(scored, key=lambda x: x[1], reverse=True)
        ]
        return sorted_sentences[:max_sentences]
