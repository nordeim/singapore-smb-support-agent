"""Document parsing using MarkItDown library."""

from markitdown import MarkItDown


class DocumentParser:
    """Document parser supporting multiple formats."""

    SUPPORTED_FORMATS = [
        ".pdf",
        ".docx",
        ".doc",
        ".xlsx",
        ".xls",
        ".pptx",
        ".ppt",
        ".html",
        ".md",
        ".txt",
        ".csv",
    ]

    @staticmethod
    def parse(file_path: str) -> str | None:
        """Parse document and return text content."""
        try:
            md = MarkItDown()
            result = md.convert(file_path)
            return result.text_content
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """Check if file format is supported."""
        import os

        _, ext = os.path.splitext(file_path)
        return ext.lower() in DocumentParser.SUPPORTED_FORMATS

    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """Extract metadata from file path."""
        import os
        from datetime import datetime

        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)

        return {
            "file_name": filename,
            "file_extension": ext.lower().lstrip("."),
            "file_size": os.path.getsize(file_path),
            "created_at": datetime.utcnow().isoformat(),
        }
