"""Store and search chunk embeddings in ChromaDB."""

import logging

import chromadb

from core.chunker import Chunk

logger = logging.getLogger(__name__)


class VectorStore:
    """Wraps a ChromaDB collection."""

    def __init__(
        self,
        collection_name: str = "internal_docs",
        host: str = "localhost",
        port: int = 8000,
    ) -> None:
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Store chunks and their vectors, replacing any with the same id."""
        if not chunks:
            logger.warning("Nothing to upsert")
            return

        self.collection.upsert(
            ids=[f"{chunk.path}::{chunk.chunk_index}" for chunk in chunks],
            embeddings=vectors,
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {
                    "filename": chunk.filename,
                    "path": chunk.path,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
        )

    def query(self, vector: list[float], top_k: int = 3) -> list[dict[str, object]]:
        """Find the most similar stored chunks to a query vector."""
        result = self.collection.query(query_embeddings=[vector], n_results=top_k)

        return [
            {
                "text": document,
                "metadata": metadata,
                "distance": distance,
            }
            for document, metadata, distance in zip(
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0],
                strict=True,
            )
        ]

    def count(self) -> int:
        """How many chunks are stored."""
        return self.collection.count()