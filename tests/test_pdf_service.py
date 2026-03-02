"""Tests for PDF processing service."""

import pytest
from app.services.pdf_service import PDFService


class TestPDFService:

    def setup_method(self):
        self.service = PDFService()

    def test_validate_accepts_valid_pdf(self):
        self.service.validate_file("paper.pdf", 1024 * 1024)

    def test_validate_rejects_non_pdf(self):
        with pytest.raises(ValueError, match="Invalid file type"):
            self.service.validate_file("document.docx", 1024)

    def test_validate_rejects_oversized_file(self):
        with pytest.raises(ValueError, match="File too large"):
            self.service.validate_file("large.pdf", 100 * 1024 * 1024)

    def test_clean_text_removes_excessive_whitespace(self):
        dirty = "Hello\n\n\n\n\nWorld   with    spaces"
        cleaned = self.service._clean_text(dirty)
        assert "\n\n\n" not in cleaned
        assert "   " not in cleaned