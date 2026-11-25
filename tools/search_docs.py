"""Document search exposed as a tool an LLM can choose to call."""

import logging
from typing import Any

from google.genai import types

from core.embedder import Embedder
from core.prompt_templates import format_context
from services.vector_store import VectorStore

logger = logging.getLogger(__name__)

TOOL_NAME = "search_internal_docs"

TOOL_DESCRIPTION = (
    "Search this company's internal engineering documentation and return the "
    "most relevant passages, each labelled with its source filename. The corpus "
    "covers API specifications, architecture decision records (ADRs), deployment "
    "runbooks, ingestion procedures and operational SOPs. Use this tool whenever a "
    "question concerns how this company's own systems are designed, configured or "
    "operated - for example authentication and token lifetimes, rollback "
    "thresholds, deployment steps, or where a particular document lives. Do not "
    "use it for general programming knowledge, for questions about public "
    "libraries, or for anything unrelated to this company's systems."
)

QUERY_DESCRIPTION = (
    "The search phrase, in natural language. Use the wording of the user's "
    "question or a focused rephrasing of it, for example 'token expiry' or "
    "'rollback error rate threshold'."
)

NO_RESULTS_MESSAGE = "No relevant passages were found in the internal documentation."

# Chroma always returns top_k matches however distant, so relevance is decided
# here. Measured on the current corpus: relevant queries match at 0.46-0.85,
# unrelated ones at 1.03 or worse. 0.95 sits in the gap.
MAX_DISTANCE = 0.95


class SearchDocsTool:
    """Wraps vector retrieval so an LLM can invoke it by name."""

    name = TOOL_NAME
    description = TOOL_DESCRIPTION

    def __init__(self, embedder: Embedder, store: VectorStore) -> None:
        self.embedder = embedder
        self.store = store

    def search(self, query: str, top_k: int = 3) -> str:
        """Retrieve the passages most relevant to a query, as formatted text."""
        logger.info("Tool %s called with query=%r", self.name, query)

        vector = self.embedder.embed([query])[0]
        matches: list[dict[str, Any]] = self.store.query(vector, top_k=top_k)

        logger.info(
            "Tool %s distances: %s",
            self.name,
            [round(match["distance"], 3) for match in matches],
        )

        relevant = [match for match in matches if match["distance"] < MAX_DISTANCE]

        if not relevant:
            logger.info(
                "Tool %s found no match under distance %.2f (best was %.2f)",
                self.name,
                MAX_DISTANCE,
                matches[0]["distance"] if matches else float("inf"),
            )
            return NO_RESULTS_MESSAGE

        logger.info("Tool %s returning %d of %d matches", self.name, len(relevant), len(matches))
        return format_context(relevant)

    @property
    def declaration(self) -> types.FunctionDeclaration:
        """The schema the model reads to decide whether to call this tool."""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description=QUERY_DESCRIPTION,
                    ),
                },
                required=["query"],
            ),
        )
