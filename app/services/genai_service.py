"""
GenAI Service — Groq
----------------------
Uses Groq API for fast, free LLM inference.
Groq runs open-source models (LLaMA, Mixtral) on custom hardware.
Free tier: 30 requests/minute, 14400 requests/day.
"""

import time
from typing import Optional
from groq import Groq

from core.config import get_settings
from core.logging_config import get_logger
from app.prompts.templates import SYSTEM_PROMPT, format_prompt

logger = get_logger(__name__)


class GenAIService:
    """Service for interacting with Groq LLM API."""

    def __init__(self):
        self.settings = get_settings()
        self.client = Groq(api_key=self.settings.groq_api_key)
        self.model_name = "llama-3.1-8b-instant"

        logger.info("genai_service_initialized", model=self.model_name)

    def count_tokens(self, text: str) -> int:
        """Estimate token count. Roughly 4 characters per token."""
        return len(text) // 4

    def _validate_token_budget(self, prompt: str, context: str = "") -> bool:
        """Verify total input does not exceed the token limit."""
        total_tokens = self.count_tokens(prompt) + self.count_tokens(context)
        max_tokens = self.settings.max_input_tokens

        if total_tokens > max_tokens:
            raise ValueError(
                f"Input too long: {total_tokens} estimated tokens "
                f"(maximum allowed: {max_tokens}). "
                f"Try a shorter question or a smaller document."
            )
        return True

    async def generate_response(
        self,
        user_prompt: str,
        context: str = "",
        system_prompt: str = SYSTEM_PROMPT,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """Send a prompt to Groq and return the response."""
        self._validate_token_budget(user_prompt, context)

        if max_tokens is None:
            max_tokens = self.settings.max_output_tokens

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
            )

            latency_ms = (time.time() - start_time) * 1000
            content = response.choices[0].message.content
            usage = response.usage

            token_data = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }

            logger.info(
                "llm_call_success",
                model=self.model_name,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                latency_ms=round(latency_ms, 2),
            )

            return {
                "content": content,
                "tokens_used": token_data,
                "latency_ms": round(latency_ms, 2),
                "model": self.model_name,
            }

        except Exception as e:
            error_str = str(e)
            logger.error("llm_error", error=error_str)
            raise RuntimeError(f"AI service error: {error_str}")

    async def summarize_paper(self, context: str) -> dict:
        prompt = format_prompt("summarize", context=context)
        return await self.generate_response(user_prompt=prompt, temperature=0.2)

    async def answer_question(self, question: str, context: str) -> dict:
        prompt = format_prompt("qa", context=context, question=question)
        return await self.generate_response(user_prompt=prompt, temperature=0.1)

    async def extract_key_findings(self, context: str) -> dict:
        prompt = format_prompt("key_findings", context=context)
        return await self.generate_response(user_prompt=prompt, temperature=0.2)

    async def analyze_methodology(self, context: str) -> dict:
        prompt = format_prompt("methodology", context=context)
        return await self.generate_response(user_prompt=prompt, temperature=0.2)


_genai_service: Optional[GenAIService] = None


def get_genai_service() -> GenAIService:
    global _genai_service
    if _genai_service is None:
        _genai_service = GenAIService()
    return _genai_service