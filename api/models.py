"""Request and response shapes for the API."""

from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    """What a caller sends."""

    query: str = Field(min_length=1, description="The natural language question")
    top_k: int = Field(default=3, ge=1, le=20, description="How many chunks to return")


class RetrievedChunk(BaseModel):
    """One matching chunk and where it came from."""

    text: str
    filename: str
    path: str
    chunk_index: int
    distance: float


class RetrieveResponse(BaseModel):
    """What the caller gets back."""

    query: str
    results: list[RetrievedChunk]