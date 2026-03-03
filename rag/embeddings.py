"""
Embedding Service — Local
---------------------------
Uses sentence-transformers to generate embeddings locally.
No API calls. No rate limits. No cost. Runs on your CPU.
"""

from core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Generates text embeddings locally using sentence-transformers."""

    def __init__(self):
        # Lazy import to prevent CI failures
        from sentence_transformers import SentenceTransformer

        logger.info("loading_embedding_model")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("embedding_model_loaded", model="all-MiniLM-L6-v2")

    def get_embedding(self, text: str) -> list[float]:
        text = text.replace("\n", " ").strip()
        if not text:
            text = "empty"

        embedding = self.model.encode(text)
        return embedding.tolist()

    def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        cleaned = [t.replace("\n", " ").strip() or "empty" for t in texts]
        embeddings = self.model.encode(cleaned)

        logger.info(
            "embeddings_generated",
            count=len(texts),
            model="all-MiniLM-L6-v2",
        )
        return [emb.tolist() for emb in embeddings]


_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
