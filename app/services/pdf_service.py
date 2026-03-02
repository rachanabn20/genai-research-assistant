"""
PDF Processing Service
------------------------
Validates, saves, and extracts text from uploaded PDF files.
"""

import os
import re
import uuid
from pathlib import Path
from typing import Optional

from PyPDF2 import PdfReader

from core.config import get_settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class PDFService:
    """Handles PDF file operations: validation, storage, text extraction."""

    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    def validate_file(self, filename: str, file_size: int) -> None:
        """
        Validate that the uploaded file is an acceptable PDF.
        Raises ValueError if validation fails.
        """
        if not filename.lower().endswith(".pdf"):
            raise ValueError(
                f"Invalid file type: '{filename}'. Only PDF files are accepted."
            )

        max_size = self.settings.max_file_size_bytes
        if file_size > max_size:
            raise ValueError(
                f"File too large: {file_size / (1024*1024):.1f}MB. "
                f"Maximum allowed: {self.settings.max_file_size_mb}MB."
            )

    def save_pdf(self, file_content: bytes, filename: str) -> tuple[str, str]:
        """
        Save uploaded PDF to disk with a unique identifier.

        Returns:
            Tuple of (paper_id, file_path)
        """
        paper_id = f"paper_{uuid.uuid4().hex[:12]}"
        safe_filename = f"{paper_id}.pdf"
        file_path = self.upload_dir / safe_filename

        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(
            "pdf_saved",
            paper_id=paper_id,
            original_filename=filename,
            size_bytes=len(file_content),
        )
        return paper_id, str(file_path)

    def extract_text(self, file_path: str) -> tuple[str, int]:
        """
        Extract all text content from a PDF file.

        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            reader = PdfReader(file_path)
            pages = len(reader.pages)
            text_parts = []

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"\n--- Page {i + 1} ---\n{page_text}")

            full_text = "\n".join(text_parts)
            full_text = self._clean_text(full_text)

            if not full_text.strip():
                raise ValueError(
                    "Could not extract text from this PDF. "
                    "It might be a scanned document (image-based). "
                    "Please upload a text-based PDF."
                )

            logger.info(
                "pdf_text_extracted",
                file_path=file_path,
                pages=pages,
                characters=len(full_text),
            )
            return full_text, pages

        except Exception as e:
            logger.error("pdf_extraction_failed", file_path=file_path, error=str(e))
            raise

    def _clean_text(self, text: str) -> str:
        """Remove excessive whitespace and null bytes from extracted text."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = text.replace("\x00", "")
        return text.strip()

    def delete_pdf(self, paper_id: str) -> bool:
        """Delete a PDF file by its paper_id."""
        file_path = self.upload_dir / f"{paper_id}.pdf"
        if file_path.exists():
            os.remove(file_path)
            logger.info("pdf_deleted", paper_id=paper_id)
            return True
        return False


_pdf_service: Optional[PDFService] = None


def get_pdf_service() -> PDFService:
    """Get or create the PDF service singleton."""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFService()
    return _pdf_service