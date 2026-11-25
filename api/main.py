"""FastAPI application exposing retrieval over the document collection."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.models import (
    ChatRequest,
    ChatResponse,
    Citation,
    ErrorResponse,
    RetrievedChunk,
    RetrieveRequest,
    RetrieveResponse,
)
from core.embedder import Embedder
from core.prompt_templates import REFUSAL_MESSAGE, format_context
from services.llm_service import FAILURE_MESSAGE, LLMService
from services.vector_store import VectorStore

logger = logging.getLogger(__name__)

embedder: Embedder | None = None
store: VectorStore | None = None
llm: LLMService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Load the model and connect to Chroma once, when the server starts."""
    logging.basicConfig(level=logging.INFO)
    for noisy in (
        "httpx",
        "httpx2",
        "httpcore",
        "google_genai",
        "sentence_transformers",
        "transformers",
        "huggingface_hub",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    global embedder, store, llm

    logger.info("Loading embedding model")
    embedder = Embedder()
    store = VectorStore()
    llm = LLMService()
    logger.info("Ready — collection holds %d chunks", store.count())

    yield

    embedder = None
    store = None
    llm = None


app = FastAPI(title="Internal Docs QA", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return our own error shape instead of FastAPI's default."""
    first = exc.errors()[0]
    parts = [str(part) for part in first["loc"] if part != "body"]
    field = ".".join(parts) if parts else "body"

    logger.warning("Validation failed on %s: %s", field, first["msg"])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="validation_error",
            message=first["msg"],
            field=field,
        ).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Return our error shape for FastAPI's own errors (404, 405, ...)."""
    logger.warning("HTTP %d on %s %s", exc.status_code, request.method, request.url.path)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="http_error",
            message=str(exc.detail),
        ).model_dump(exclude_none=True),
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
        ).model_dump(exclude_none=True),
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.post(
    "/api/v1/retrieve",
    response_model=RetrieveResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        405: {"model": ErrorResponse, "description": "Method not allowed"},
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


@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        405: {"model": ErrorResponse, "description": "Method not allowed"},
        422: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "LLM provider unavailable"},
        500: {"model": ErrorResponse, "description": "Unexpected error"},
    },
)
def chat(request: ChatRequest) -> ChatResponse:
    """Answer a question from the document collection, with sources."""
    if embedder is None or store is None or llm is None:
        raise RuntimeError("Service not initialised")

    vector = embedder.embed([request.question])[0]
    matches = store.query(vector, top_k=request.top_k)
    context = format_context(matches)
    answer = llm.generate_response(context, request.question)

    if answer == FAILURE_MESSAGE:
        logger.error("LLM unavailable for %r", request.question)
        raise HTTPException(status_code=503, detail=FAILURE_MESSAGE)

    if answer.strip() == REFUSAL_MESSAGE:
        logger.info("Refused: no grounded answer for %r", request.question)
        return ChatResponse(question=request.question, answer=answer, citations=[])

    citations = [
        Citation(
            filename=match["metadata"]["filename"],
            path=match["metadata"]["path"],
            chunk_index=match["metadata"]["chunk_index"],
        )
        for match in matches
    ]

    return ChatResponse(question=request.question, answer=answer, citations=citations)
