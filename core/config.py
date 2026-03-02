"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):

    # Groq (free LLM provider)
    groq_api_key: str = Field(..., description="Groq API key")

    # Kept for compatibility but not used
    gemini_api_key: str = Field(default="not-needed")
    openai_api_key: str = Field(default="not-needed")
    openai_model: str = Field(default="llama-3.1-8b-instant")
    openai_embedding_model: str = Field(default="local")

    # Application
    app_name: str = Field(default="AI Research Paper Assistant")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)

    # Security
    api_key_secret: str = Field(default="default-secret-change-me")
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000"
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=20)

    # RAG
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    max_context_chunks: int = Field(default=5)

    # Token Limits
    max_input_tokens: int = Field(default=4000)
    max_output_tokens: int = Field(default=2000)

    # Uploads
    max_file_size_mb: int = Field(default=10)
    upload_dir: str = Field(default="uploads")

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()