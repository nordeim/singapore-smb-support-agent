"""CLI tool for document ingestion into Qdrant vector database."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion.pipeline import IngestionPipeline, IngestionResult
from app.rag.qdrant_client import QdrantManager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into Qdrant vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest single file
  python -m backend.scripts.ingest_documents --input-files document.pdf

  # Ingest multiple files
  python -m backend.scripts.ingest_documents --input-files file1.pdf,file2.docx

  # Ingest entire directory
  python -m backend.scripts.ingest_documents --input-dir ./documents

  # Ingest directory recursively
  python -m backend.scripts.ingest_documents --input-dir ./documents --recursive

  # Use recursive chunking strategy
  python -m backend.scripts.ingest_documents --input-dir ./documents --chunk-strategy recursive

  # Ingest with custom collection name
  python -m backend.scripts.ingest_documents --input-dir ./documents --collection custom_kb
        """,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input-files",
        type=str,
        help="Comma-separated list of file paths to ingest",
    )
    input_group.add_argument(
        "--input-dir",
        type=str,
        help="Directory path containing documents to ingest",
    )

    parser.add_argument(
        "--collection",
        type=str,
        default="knowledge_base",
        help="Qdrant collection name (default: knowledge_base)",
    )
    parser.add_argument(
        "--chunk-strategy",
        type=str,
        choices=["semantic", "recursive"],
        default="semantic",
        help="Chunking strategy (default: semantic)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of concurrent document ingestions (default: 10)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan input directory for documents",
    )
    parser.add_argument(
        "--file-extensions",
        type=str,
        default=None,
        help="Comma-separated list of file extensions to process (default: all supported)",
    )
    parser.add_argument(
        "--metadata",
        type=str,
        default=None,
        help="JSON string with additional metadata to add to all documents",
    )
    parser.add_argument(
        "--init-collections",
        action="store_true",
        help="Initialize Qdrant collections before ingestion",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--use-mock-embeddings",
        action="store_true",
        help="Use mock embeddings instead of real API (for testing)",
    )

    return parser.parse_args()


def parse_metadata(metadata_str: str) -> dict | None:
    """Parse metadata JSON string."""
    if not metadata_str:
        return None

    try:
        return json.loads(metadata_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing metadata JSON: {e}")
        return None

    try:
        import json

        return json.loads(metadata_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing metadata JSON: {e}")
        return None

    try:
        import json

        return json.loads(metadata_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing metadata JSON: {e}")
        return None


async def ingest_single_file(
    file_path: str,
    pipeline: IngestionPipeline,
    verbose: bool = False,
) -> dict:
    """Ingest a single document."""
    print(f"Processing: {file_path}")
    result = await pipeline.ingest_document(file_path)

    if verbose or not result.get("success"):
        print(f"  Result: {result.get('success')}")
        if not result.get("success"):
            print(f"  Error: {result.get('error')}")
        else:
            print(f"  Chunks: {result.get('chunks_processed', 0)}")
            print(f"  Points: {result.get('points_upserted', 0)}")

    return result


async def ingest_files(
    file_paths: list[str],
    pipeline: IngestionPipeline,
    batch_size: int,
    verbose: bool = False,
) -> IngestionResult:
    """Ingest multiple files."""
    print(f"\nProcessing {len(file_paths)} files (batch size: {batch_size})")
    print("=" * 80)

    result = await pipeline.ingest_batch(
        file_paths=file_paths,
        batch_size=batch_size,
    )

    return result


async def ingest_directory(
    directory_path: str,
    pipeline: IngestionPipeline,
    recursive: bool,
    batch_size: int,
    file_extensions: list[str] | None = None,
    verbose: bool = False,
) -> IngestionResult:
    """Ingest all documents from a directory."""
    print(f"\nProcessing directory: {directory_path}")
    if recursive:
        print("Recursive scan: enabled")
    print("=" * 80)

    result = await pipeline.ingest_directory(
        directory_path=directory_path,
        recursive=recursive,
        batch_size=batch_size,
        file_extensions=file_extensions,
    )

    return result


def print_summary(result: IngestionResult):
    """Print ingestion summary."""
    print("\n" + "=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print(f"Total Documents: {result.total_documents}")
    print(f"Successful: {result.successful}")
    print(f"Failed: {result.failed}")
    print(f"Total Chunks: {result.total_chunks}")

    if result.errors:
        print("\nErrors:")
        for i, error in enumerate(result.errors[:10], 1):
            print(f"  {i}. {error}")
        if len(result.errors) > 10:
            print(f"  ... and {len(result.errors) - 10} more errors")

    print("=" * 80)


async def main():
    """Main entry point."""
    args = parse_arguments()

    print("=" * 80)
    print("DOCUMENT INGESTION TOOL")
    print("=" * 80)
    print(f"Collection: {args.collection}")
    print(f"Chunk Strategy: {args.chunk_strategy}")
    print(f"Batch Size: {args.batch_size}")
    if args.use_mock_embeddings:
        print("Embeddings: MOCK (testing mode)")
    else:
        print("Embeddings: API (requires valid key)")
    print("=" * 80)

    if args.init_collections:
        print("\nInitializing Qdrant collections...")
        QdrantManager.initialize_collections()
        print("Collections initialized.")

    parse_metadata(args.metadata)

    pipeline = IngestionPipeline(
        chunk_strategy=args.chunk_strategy,
        collection_name=args.collection,
        use_mock_embeddings=args.use_mock_embeddings,
    )

    result: IngestionResult = None

    try:
        if args.input_files:
            file_paths = [fp.strip() for fp in args.input_files.split(",")]

            if len(file_paths) == 1:
                single_result = await ingest_single_file(
                    file_path=file_paths[0],
                    pipeline=pipeline,
                    verbose=args.verbose,
                )

                if single_result.get("success"):
                    result = IngestionResult(
                        total_documents=1,
                        successful=1,
                        failed=0,
                        total_chunks=single_result.get("chunks_processed", 0),
                    )
                else:
                    result = IngestionResult(
                        total_documents=1,
                        successful=0,
                        failed=1,
                        total_chunks=0,
                        errors=[single_result.get("error", "Unknown error")],
                    )
            else:
                result = await ingest_files(
                    file_paths=file_paths,
                    pipeline=pipeline,
                    batch_size=args.batch_size,
                    verbose=args.verbose,
                )

        elif args.input_dir:
            file_extensions: list[str] | None = None
            if args.file_extensions:
                file_extensions = [ext.strip() for ext in args.file_extensions.split(",")]

            result = await ingest_directory(
                directory_path=args.input_dir,
                pipeline=pipeline,
                recursive=args.recursive,
                batch_size=args.batch_size,
                file_extensions=file_extensions,
                verbose=args.verbose,
            )

        if result:
            print_summary(result)

            if result.successful > 0:
                print("\n✅ Ingestion completed successfully!")
            else:
                print("\n❌ Ingestion completed with errors.")
                sys.exit(1)
        else:
            print("\n❌ No documents were processed.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
