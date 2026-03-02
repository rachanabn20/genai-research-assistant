"""
Vector Store — ChromaDB Integration
--------------------------------------
Stores text chunks as vectors and retrieves the most relevant ones
for a given query using semantic similarity search.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional

from core.config import get_settings
from core.logging_config import get_logger
from rag.embeddings import get_embedding_service

logger = get_logger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""

    def __init__(self):
        settings = get_settings()
        self.embedding_service = get_embedding_service()
        self.max_results = settings.max_context_chunks

        self.client = chromadb.Client(ChromaSettings(
            anonymized_telemetry=False,
        ))
        logger.info("vector_store_initialized")

    def _get_or_create_collection(self, paper_id: str):
        """Each paper gets its own ChromaDB collection."""
        collection_name = paper_id.replace("-", "_")
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": f"Chunks for {paper_id}"}
        )

    def store_chunks(self, chunks: list[dict], paper_id: str) -> int:
        """
        Store text chunks with their embeddings in the vector database.

        Returns the number of chunks stored.
        """
        collection = self._get_or_create_collection(paper_id)

        texts = [chunk["content"] for chunk in chunks]
        ids = [chunk["id"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        embeddings = self.embedding_service.get_embeddings_batch(texts)

        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )

        logger.info("chunks_stored", paper_id=paper_id, count=len(chunks))
        return len(chunks)

    def search(
        self, query: str, paper_id: str, n_results: Optional[int] = None
    ) -> list[dict]:
        """
        Find the most relevant chunks for a given query.

        Steps:
        1. Convert query text to an embedding vector
        2. ChromaDB finds stored vectors most similar to the query vector
        3. Return the corresponding text chunks ranked by similarity
        """
        if n_results is None:
            n_results = self.max_results

        collection = self._get_or_create_collection(paper_id)

        if collection.count() == 0:
            logger.warning("search_empty_collection", paper_id=paper_id)
            return []

        query_embedding = self.embedding_service.get_embedding(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        search_results = []
        for i in range(len(results["documents"][0])):
            search_results.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "score": 1 - results["distances"][0][i],
            })

        logger.info(
            "vector_search_completed",
            paper_id=paper_id,
            query_preview=query[:50],
            results_count=len(search_results),
        )
        return search_results

    def delete_paper(self, paper_id: str) -> bool:
        """Delete all stored vectors for a paper."""
        try:
            collection_name = paper_id.replace("-", "_")
            self.client.delete_collection(collection_name)
            logger.info("paper_vectors_deleted", paper_id=paper_id)
            return True
        except Exception:
            return False

    def paper_exists(self, paper_id: str) -> bool:
        """Check if a paper has been indexed in the vector store."""
        try:
            collection_name = paper_id.replace("-", "_")
            collection = self.client.get_collection(collection_name)
            return collection.count() > 0
        except Exception:
            return False


_vector_store = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store