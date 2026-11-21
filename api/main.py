"""FastAPI application exposing retrieval over the document collection."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.models import ErrorResponse, RetrievedChunk, RetrieveRequest, RetrieveResponse
from core.embedder import Embedder
from services.vector_store import VectorStore

logger = logging.getLogger(__name__)

embedder: Embedder | None = None
store: VectorStore | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Load the model and connect to Chroma once, when the server starts."""
    logging.basicConfig(level=logging.INFO)
    for noisy in ("httpx", "httpcore", "sentence_transformers", "transformers", "huggingface_hub"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    global embedder, store

    logger.info("Loading embedding model")
    embedder = Embedder()
    store = VectorStore()
    logger.info("Ready — collection holds %d chunks", store.count())

    yield

    embedder = None
    store = None


app = FastAPI(title="Internal Docs QA", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return our own error shape instead of FastAPI's default."""
    first = exc.errors()[0]
    field = ".".join(str(part) for part in first["loc"] if part != "body")

    logger.warning("Validation failed on %s: %s", field, first["msg"])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="validation_error",
            message=first["msg"],
            field=field,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch anything unexpected without leaking internals."""
    logger.exception("Unhandled error on %s", request.url.path)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_error",
            message="Something went wrong processing this request.",
        ).model_dump(),
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.post(
    "/api/v1/retrieve",
    response_model=RetrieveResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Unexpected error"},
    },
)
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