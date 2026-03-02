"""Tests for prompt templates."""

import pytest
from app.prompts.templates import get_prompt, format_prompt, SYSTEM_PROMPT


class TestPromptTemplates:

    def test_system_prompt_exists_and_is_substantial(self):
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 100

    def test_system_prompt_has_guardrails(self):
        prompt_lower = SYSTEM_PROMPT.lower()
        assert "never" in prompt_lower

    def test_get_valid_prompt_types(self):
        for prompt_type in ["summarize", "qa", "key_findings", "methodology"]:
            prompt = get_prompt(prompt_type)
            assert prompt is not None
            assert len(prompt) > 50

    def test_get_invalid_prompt_type_raises_error(self):
        with pytest.raises(ValueError, match="Unknown prompt type"):
            get_prompt("nonexistent_type")

    def test_format_qa_prompt_with_all_variables(self):
        formatted = format_prompt(
            "qa",
            context="This is paper content about neural networks.",
            question="What architecture was used?",
        )
        assert "neural networks" in formatted
        assert "What architecture was used?" in formatted

    def test_format_summarize_prompt(self):
        formatted = format_prompt(
            "summarize",
            context="A study on climate change effects.",
        )
        assert "climate change" in formatted

    def test_format_prompt_with_missing_variable_raises_error(self):
        with pytest.raises(ValueError, match="Missing required variable"):
            format_prompt("qa", context="test")

    def test_all_prompts_have_context_placeholder(self):
        for prompt_type in ["summarize", "qa", "key_findings", "methodology"]:
            prompt = get_prompt(prompt_type)
            assert "{context}" in prompt