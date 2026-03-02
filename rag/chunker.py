"""
Text Chunking Module
----------------------
Splits long text into overlapping chunks for RAG processing.
RecursiveCharacterTextSplitter tries to split at natural boundaries
(paragraphs first, then sentences, then words) to keep chunks coherent.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import get_settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class TextChunker:
    """Splits long text into overlapping chunks."""

    def __init__(self):
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            is_separator_regex=False,
        )

    def chunk_text(self, text: str, paper_id: str) -> list[dict]:
        """
        Split text into chunks with metadata.

        Args:
            text: Full paper text
            paper_id: Unique paper identifier

        Returns:
            List of dicts, each with 'content', 'metadata', and 'id'
        """
        chunks = self.splitter.split_text(text)

        chunked_docs = []
        for i, chunk in enumerate(chunks):
            chunked_docs.append({
                "content": chunk,
                "metadata": {
                    "paper_id": paper_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "char_count": len(chunk),
                },
                "id": f"{paper_id}_chunk_{i}",
            })

        logger.info(
            "text_chunked",
            paper_id=paper_id,
            total_chunks=len(chunks),
            avg_chunk_size=sum(len(c) for c in chunks) // max(len(chunks), 1),
        )
        return chunked_docs


_chunker = None


def get_chunker() -> TextChunker:
    global _chunker
    if _chunker is None:
        _chunker = TextChunker()
    return _chunker