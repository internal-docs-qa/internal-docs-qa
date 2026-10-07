"""Turn text into vectors using a sentence-transformers model."""

import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder:
    """Converts text into embedding vectors."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.max_tokens = self.model.max_seq_length

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Convert a list of texts into a list of vectors."""
        vectors = self.model.encode(texts, batch_size=32, show_progress_bar=False)
        return [vector.tolist() for vector in vectors]

    def dimensions(self) -> int:
        """How many numbers each vector has."""
        return int(self.model.get_sentence_embedding_dimension())