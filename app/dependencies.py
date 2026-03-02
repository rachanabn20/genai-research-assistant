"""
FastAPI Dependencies
----------------------
Functions that run before route handlers to provide required services.
"""

from app.services.rag_service import get_rag_service, RAGService


async def get_rag() -> RAGService:
    """Provide the RAG service to route handlers."""
    return get_rag_service()