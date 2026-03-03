"""
RAG Orchestration Service
----------------------------
Coordinates the full pipeline:
  Upload: PDF -> Extract text -> Chunk -> Embed -> Store
  Query:  Question -> Search similar chunks -> LLM generates answer
"""

#from typing import Optional

from core.logging_config import get_logger
from app.services.pdf_service import get_pdf_service
from app.services.genai_service import get_genai_service
from rag.chunker import get_chunker
from rag.vector_store import get_vector_store

logger = get_logger(__name__)


class RAGService:
    """Orchestrates the full RAG pipeline for paper processing and querying."""

    def __init__(self):
        self.pdf_service = get_pdf_service()
        self.genai_service = get_genai_service()
        self.chunker = get_chunker()
        self.vector_store = get_vector_store()

    async def ingest_paper(self, file_content: bytes, filename: str) -> dict:
        """
        Full paper ingestion pipeline.

        Steps:
        1. Validate the uploaded file
        2. Save the PDF to disk
        3. Extract text from the PDF
        4. Split text into chunks
        5. Generate embeddings and store in vector database

        Returns dict with paper_id, filename, pages, and chunks count.
        """
        self.pdf_service.validate_file(filename, len(file_content))
        paper_id, file_path = self.pdf_service.save_pdf(file_content, filename)

        try:
            text, pages = self.pdf_service.extract_text(file_path)
            chunks = self.chunker.chunk_text(text, paper_id)
            stored_count = self.vector_store.store_chunks(chunks, paper_id)

            logger.info(
                "paper_ingested",
                paper_id=paper_id,
                filename=filename,
                pages=pages,
                chunks=stored_count,
            )

            return {
                "paper_id": paper_id,
                "filename": filename,
                "pages": pages,
                "chunks": stored_count,
            }

        except Exception as e:
            # Clean up if anything fails after saving
            self.pdf_service.delete_pdf(paper_id)
            self.vector_store.delete_paper(paper_id)
            logger.error("paper_ingestion_failed", paper_id=paper_id, error=str(e))
            raise

    async def ask_question(self, paper_id: str, question: str) -> dict:
        """
        Answer a question about a paper using RAG.

        Steps:
        1. Search vector database for chunks relevant to the question
        2. Combine those chunks into a context string
        3. Send context + question to the LLM
        4. Return the answer with source references
        """
        if not self.vector_store.paper_exists(paper_id):
            raise ValueError(
                f"Paper '{paper_id}' not found. Please upload it first."
            )

        search_results = self.vector_store.search(question, paper_id)

        if not search_results:
            raise ValueError(
                f"No content found for paper '{paper_id}'. "
                "The paper may not have been processed correctly."
            )

        context = "\n\n---\n\n".join(
            [result["content"] for result in search_results]
        )
        sources = [result["content"][:200] + "..." for result in search_results]

        response = await self.genai_service.answer_question(
            question=question, context=context
        )

        return {
            "paper_id": paper_id,
            "question": question,
            "answer": response["content"],
            "sources": sources,
            "model": response["model"],
            "tokens_used": response["tokens_used"],
            "latency_ms": response["latency_ms"],
        }

    async def analyze_paper(self, paper_id: str, analysis_type: str) -> dict:
        """
        Perform analysis on a paper (summarize, key_findings, methodology).
        Retrieves more chunks than Q&A to get a broader view of the paper.
        """
        if not self.vector_store.paper_exists(paper_id):
            raise ValueError(
                f"Paper '{paper_id}' not found. Please upload it first."
            )

        query_map = {
            "summarize": "main research objective methodology results conclusions",
            "key_findings": "key findings results discoveries contributions",
            "methodology": "methodology methods approach techniques data collection",
        }

        query = query_map.get(analysis_type, "research overview")
        search_results = self.vector_store.search(query, paper_id, n_results=8)

        context = "\n\n---\n\n".join(
            [result["content"] for result in search_results]
        )

        analysis_methods = {
            "summarize": self.genai_service.summarize_paper,
            "key_findings": self.genai_service.extract_key_findings,
            "methodology": self.genai_service.analyze_methodology,
        }

        method = analysis_methods.get(analysis_type)
        if not method:
            raise ValueError(f"Unknown analysis type: '{analysis_type}'")

        response = await method(context=context)

        return {
            "paper_id": paper_id,
            "analysis_type": analysis_type,
            "content": response["content"],
            "model": response["model"],
            "tokens_used": response["tokens_used"],
            "latency_ms": response["latency_ms"],
        }


_rag_service = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service