"""Store and search chunk embeddings in ChromaDB."""

import logging
from typing import Any, cast

import chromadb

from core.chunker import Chunk
from core.config import COLLECTION_NAME

logger = logging.getLogger(__name__)


class VectorStore:
    """Wraps a ChromaDB collection."""

    def __init__(
        self,
        collection_name: str = COLLECTION_NAME,
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
            embeddings=cast(Any, vectors),
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

    def query(self, vector: list[float], top_k: int = 3) -> list[dict[str, Any]]:
        """Find the most similar stored chunks to a query vector."""
        result = self.collection.query(query_embeddings=cast(Any, [vector]), n_results=top_k)

        documents = result["documents"]
        metadatas = result["metadatas"]
        distances = result["distances"]

        if documents is None or metadatas is None or distances is None:
            return []

        return [
            {
                "text": document,
                "metadata": metadata,
                "distance": distance,
            }
            for document, metadata, distance in zip(
                documents[0],
                metadatas[0],
                distances[0],
                strict=True,
            )
        ]

    def count(self) -> int:
        """How many chunks are stored."""
        return self.collection.count()