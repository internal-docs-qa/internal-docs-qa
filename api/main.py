"""FastAPI application exposing retrieval over the document collection."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.models import RetrievedChunk, RetrieveRequest, RetrieveResponse
from core.embedder import Embedder
from services.vector_store import VectorStore

logger = logging.getLogger(__name__)

embedder: Embedder | None = None
store: VectorStore | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Load the model and connect to Chroma once, when the server starts."""
    logging.basicConfig(level=logging.INFO)
    global embedder, store

    logger.info("Loading embedding model")
    embedder = Embedder()
    store = VectorStore()
    logger.info("Ready — collection holds %d chunks", store.count())

    yield

    embedder = None
    store = None


app = FastAPI(title="Internal Docs QA", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.post("/api/v1/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    """Find the chunks most similar to a query."""
    if embedder is None or store is None:
        raise RuntimeError("Service not initialised")

    vector = embedder.embed([request.query])[0]
    matches = store.query(vector, top_k=request.top_k)

    results = [
        RetrievedChunk(
            text=match["text"],
            filename=match["metadata"]["filename"],
            path=match["metadata"]["path"],
            chunk_index=match["metadata"]["chunk_index"],
            distance=match["distance"],
        )
        for match in matches
    ]

    return RetrieveResponse(query=request.query, results=results)
