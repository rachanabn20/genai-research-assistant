"""
Pydantic Schemas — Data Contracts
-----------------------------------
Define the exact structure of API requests and responses.
Pydantic validates all incoming data automatically.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AnalysisType(str, Enum):
    """Types of analysis the AI can perform on a paper."""
    SUMMARIZE = "summarize"
    KEY_FINDINGS = "key_findings"
    METHODOLOGY = "methodology"


# -- Request Models --

class QuestionRequest(BaseModel):
    """What the client sends when asking a question about a paper."""

    paper_id: str = Field(
        ...,
        description="ID of the uploaded paper",
        examples=["paper_abc123def456"]
    )
    question: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Question to ask about the paper",
        examples=["What methodology was used in this study?"]
    )


class AnalysisRequest(BaseModel):
    """What the client sends when requesting paper analysis."""

    paper_id: str = Field(
        ...,
        description="ID of the uploaded paper"
    )
    analysis_type: AnalysisType = Field(
        ...,
        description="Type of analysis to perform"
    )


# -- Response Models --

class UploadResponse(BaseModel):
    """What the API returns after a successful paper upload."""

    paper_id: str
    filename: str
    pages: int
    chunks: int
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnswerResponse(BaseModel):
    """What the API returns after answering a question."""

    paper_id: str
    question: str
    answer: str
    sources: list[str] = Field(
        description="Text chunks used to generate the answer"
    )
    model: str
    tokens_used: dict
    latency_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnalysisResponse(BaseModel):
    """What the API returns after analyzing a paper."""

    paper_id: str
    analysis_type: str
    content: str
    model: str
    tokens_used: dict
    latency_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """What the health check endpoint returns."""

    status: str = "healthy"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)