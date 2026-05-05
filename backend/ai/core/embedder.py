from sentence_transformers import SentenceTransformer
from ai.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Embedder:
    """
    Singleton wrapper around SentenceTransformer.
    Loaded once at app startup via lifespan, reused on every request.
    """

    def __init__(self):
        self._model: SentenceTransformer | None = None

    def load(self):
        if self._model is None:
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")

    def embed(self, text: str) -> list[float]:
        if self._model is None:
            raise RuntimeError("Embedder not loaded. Call embedder.load() first.")
        return self._model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if self._model is None:
            raise RuntimeError("Embedder not loaded. Call embedder.load() first.")
        return self._model.encode(texts).tolist()


# Module-level singleton — imported everywhere
embedder = Embedder()
