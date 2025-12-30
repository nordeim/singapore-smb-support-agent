"""Ingestion pipeline orchestrator for document processing."""

from typing import List, Optional, Literal
from pathlib import Path
import asyncio
from datetime import datetime

from app.ingestion.parsers.markitdown_parser import DocumentParser
from app.ingestion.chunkers.chunker import SemanticChunker, RecursiveChunker
from app.ingestion.embedders.embedding import EmbeddingGenerator
from app.rag.qdrant_client import QdrantManager
from app.config import settings
from qdrant_client.http.models import PointStruct


def get_embedding_generator(use_mock: bool = False):
    """Factory function to get embedding generator."""
    if use_mock:
        from app.ingestion.embedders.mock_embedding import MockEmbeddingGenerator

        return MockEmbeddingGenerator()
    return EmbeddingGenerator()


class IngestionResult:
    """Result of ingestion operation."""

    def __init__(
        self,
        total_documents: int = 0,
        successful: int = 0,
        failed: int = 0,
        total_chunks: int = 0,
        errors: Optional[List[str]] = None,
    ):
        self.total_documents = total_documents
        self.successful = successful
        self.failed = failed
        self.total_chunks = total_chunks
        self.errors = errors or []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_documents": self.total_documents,
            "successful": self.successful,
            "failed": self.failed,
            "total_chunks": self.total_chunks,
            "errors": self.errors,
        }


class IngestionPipeline:
    """Orchestrates document ingestion pipeline."""

    def __init__(
        self,
        chunk_strategy: Literal["semantic", "recursive"] = "semantic",
        collection_name: str = "knowledge_base",
        use_mock_embeddings: bool = False,
    ):
        """
        Initialize ingestion pipeline.

        Args:
            chunk_strategy: Chunking strategy (semantic or recursive)
            collection_name: Qdrant collection name
            use_mock_embeddings: Use mock embeddings for testing
        """
        self.parser = DocumentParser()
        self.embedder = get_embedding_generator(use_mock_embeddings)
        self.qdrant = QdrantManager()
        self.collection_name = collection_name

        if chunk_strategy == "semantic":
            self.chunker = SemanticChunker(
                model_name="all-MiniLM-L6-v2",
                chunk_size=settings.CHUNK_SIZE,
                similarity_threshold=settings.CHUNK_SIMILARITY_THRESHOLD,
            )
        else:
            self.chunker = RecursiveChunker(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""],
            )

    async def ingest_document(
        self,
        file_path: str,
        additional_metadata: Optional[dict] = None,
    ) -> dict:
        """
        Ingest a single document.

        Args:
            file_path: Path to document file
            additional_metadata: Additional metadata to add

        Returns:
            Dict with ingestion result
        """
        try:
            if not self.parser.is_supported(file_path):
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "Unsupported file format",
                }

            text_content = self.parser.parse(file_path)
            if not text_content:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "Failed to parse document",
                }

            file_metadata = self.parser.extract_metadata(file_path)

            chunks = self.chunker.chunk(text_content)
            if not chunks:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "No chunks generated",
                }

            embeddings = await self.embedder.generate(chunks)

            points = self._create_qdrant_points(
                chunks=chunks,
                embeddings=embeddings,
                file_metadata=file_metadata,
                additional_metadata=additional_metadata,
            )

            await self.qdrant.upsert_documents(
                collection_name=self.collection_name,
                points=points,
            )

            return {
                "success": True,
                "file_path": file_path,
                "chunks_processed": len(chunks),
                "points_upserted": len(points),
            }

        except Exception as e:
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e),
            }

    async def ingest_batch(
        self,
        file_paths: List[str],
        batch_size: int = 10,
        additional_metadata: Optional[dict] = None,
    ) -> IngestionResult:
        """
        Ingest multiple documents in batches.

        Args:
            file_paths: List of file paths to ingest
            batch_size: Number of concurrent ingestions
            additional_metadata: Additional metadata to add to all documents

        Returns:
            IngestionResult with statistics
        """
        result = IngestionResult(total_documents=len(file_paths))

        semaphore = asyncio.Semaphore(batch_size)

        async def ingest_with_limit(file_path: str):
            async with semaphore:
                return await self.ingest_document(file_path, additional_metadata)

        tasks = [ingest_with_limit(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                result.failed += 1
                result.errors.append(f"Exception: {str(res)}")
            elif isinstance(res, dict):
                if res.get("success"):
                    result.successful += 1
                    result.total_chunks += res.get("chunks_processed", 0)
                else:
                    result.failed += 1
                    result.errors.append(
                        f"{res.get('file_path')}: {res.get('error', 'Unknown error')}"
                    )

        return result

    async def ingest_directory(
        self,
        directory_path: str,
        recursive: bool = False,
        batch_size: int = 10,
        file_extensions: Optional[List[str]] = None,
        additional_metadata: Optional[dict] = None,
    ) -> IngestionResult:
        """
        Ingest all documents from a directory.

        Args:
            directory_path: Path to directory
            recursive: Whether to scan subdirectories
            batch_size: Number of concurrent ingestions
            file_extensions: List of file extensions to process (default: all supported)
            additional_metadata: Additional metadata to add to all documents

        Returns:
            IngestionResult with statistics
        """
        dir_path = Path(directory_path)

        if not dir_path.exists() or not dir_path.is_dir():
            return IngestionResult(
                total_documents=0,
                errors=[f"Directory not found: {directory_path}"],
            )

        pattern = "**/*" if recursive else "*"

        file_paths = []
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                if file_extensions is None or file_path.suffix.lower() in [
                    ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                    for ext in file_extensions
                ]:
                    if self.parser.is_supported(str(file_path)):
                        file_paths.append(str(file_path))

        if not file_paths:
            return IngestionResult(
                total_documents=0,
                errors=[f"No supported documents found in {directory_path}"],
            )

        return await self.ingest_batch(
            file_paths=file_paths,
            batch_size=batch_size,
            additional_metadata=additional_metadata,
        )

    def _create_qdrant_points(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        file_metadata: dict,
        additional_metadata: Optional[dict] = None,
    ) -> List[PointStruct]:
        """
        Create Qdrant points from chunks and embeddings.

        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
            file_metadata: File-level metadata
            additional_metadata: Additional metadata to add

        Returns:
            List of Qdrant PointStruct objects
        """
        from uuid import uuid4

        points = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = {
                "text": chunk,
                "chunk_index": i,
                "language": "en",
                "created_at": datetime.utcnow().isoformat(),
                "file_name": file_metadata.get("file_name"),
                "file_extension": file_metadata.get("file_extension"),
                "file_size": file_metadata.get("file_size"),
            }

            if additional_metadata:
                metadata.update(additional_metadata)

            point_id = str(uuid4())

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=metadata,
                )
            )

        return points


async def get_ingestion_pipeline(
    chunk_strategy: Literal["semantic", "recursive"] = "semantic",
    collection_name: str = "knowledge_base",
) -> IngestionPipeline:
    """Factory function to create ingestion pipeline instance."""
    return IngestionPipeline(
        chunk_strategy=chunk_strategy,
        collection_name=collection_name,
    )
