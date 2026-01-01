"""Text chunking strategies for RAG."""

import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticChunker:
    """Semantic chunking using sentence embeddings."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 512,
        similarity_threshold: float = 0.5,
    ):
        """Initialize semantic chunker."""
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.similarity_threshold = similarity_threshold

    def chunk(self, text: str) -> list[str]:
        """Chunk text based on semantic boundaries."""
        sentences = self._split_sentences(text)

        if not sentences:
            return []

        embeddings = self.model.encode(sentences, convert_to_numpy=True)

        chunks = []
        current_chunk = [sentences[0]]

        for i in range(1, len(sentences)):
            similarity = self._cosine_similarity(embeddings[i - 1], embeddings[i])

            if similarity < self.similarity_threshold:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i]]
            else:
                current_chunk.append(sentences[i])

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


class RecursiveChunker:
    """Recursive character chunking as fallback."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: list[str] = ["\n\n", "\n", ". ", " ", ""],
    ):
        """Initialize recursive chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators

    def chunk(self, text: str) -> list[str]:
        """Recursively chunk text."""
        return self._recursive_split(text, self.separators)

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using separators."""
        separator = separators[0]

        if separator == "":
            return self._split_text(text, separator)

        if separator not in text:
            return self._recursive_split(text, separators[1:])

        parts = text.split(separator)
        chunks = []
        current_chunk = ""

        for part in parts:
            if len(current_chunk) + len(part) < self.chunk_size:
                current_chunk += part + separator
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                current_chunk = part + separator

        if current_chunk:
            chunks.append(current_chunk.rstrip())

        return chunks

    def _split_text(self, text: str, separator: str) -> list[str]:
        """Split text into chunks with overlap."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap

        return chunks
