"""Ingestion module for document processing."""

from app.ingestion.pipeline import IngestionPipeline, IngestionResult, get_ingestion_pipeline

__all__ = [
    "IngestionPipeline",
    "IngestionResult",
    "get_ingestion_pipeline",
]
