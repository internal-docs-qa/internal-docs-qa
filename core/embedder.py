"""Turn text into vectors using a sentence-transformers model."""

import logging

from sentence_transformers import SentenceTransformer

from core.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)



class Embedder:
    """Converts text into embedding vectors."""

    def __init__(self, model_name: str = EMBEDDING_MODEL) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.max_tokens: int = self.model.max_seq_length or 512

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Convert a list of texts into a list of vectors."""
        vectors = self.model.encode(texts, batch_size=32, show_progress_bar=False)
        return [vector.tolist() for vector in vectors]

    def dimensions(self) -> int:
        """How many numbers each vector has."""
        return self.model.get_sentence_embedding_dimension() or 0