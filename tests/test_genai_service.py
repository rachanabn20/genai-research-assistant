"""Tests for GenAI service."""

import pytest
from app.services.genai_service import GenAIService


class TestGenAIService:

    def setup_method(self):
        self.service = GenAIService()

    def test_count_tokens_returns_positive_integer(self):
        count = self.service.count_tokens("Hello world, this is a test.")
        assert count > 0
        assert isinstance(count, int)

    def test_count_tokens_empty_string(self):
        assert self.service.count_tokens("") == 0

    def test_token_budget_passes_for_short_input(self):
        result = self.service._validate_token_budget("Short prompt")
        assert result is True

    def test_token_budget_fails_for_extremely_long_input(self):
        long_text = "word " * 100000
        with pytest.raises(ValueError, match="Input too long"):
            self.service._validate_token_budget(long_text)