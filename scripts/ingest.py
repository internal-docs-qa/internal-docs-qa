"""Ingest markdown documents into ChromaDB: parse, chunk, embed, store."""

import logging

from core.chunker import Chunk, TextChunker
from core.embedder import Embedder
from core.parser import DocumentParser
from services.vector_store import VectorStore

RAW_DOCS = "raw_docs"

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpcore", "sentence_transformers", "transformers", "huggingface_hub"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    parser = DocumentParser()
    chunker = TextChunker()
    embedder = Embedder()
    store = VectorStore()

    documents = parser.parse_directory(RAW_DOCS)
    logger.info("Parsed %d documents", len(documents))

    all_chunks: list[Chunk] = []
    for document in documents:
        chunks = chunker.chunk_document(document)
        logger.info("%s -> %d chunks", document.filename, len(chunks))
        all_chunks.extend(chunks)

    if not all_chunks:
        logger.warning("No chunks produced, nothing to store")
        return

    oversized = [c for c in all_chunks if chunker.count_tokens(c.text) > embedder.max_tokens]
    if oversized:
        logger.warning(
            "%d of %d chunks exceed the model's %d-token limit and will be truncated",
            len(oversized),
            len(all_chunks),
            embedder.max_tokens,
        )

    vectors = embedder.embed([chunk.text for chunk in all_chunks])
    logger.info("Embedded %d chunks into %d-dimension vectors", len(vectors), len(vectors[0]))

    store.upsert(all_chunks, vectors)
    logger.info("Collection now holds %d chunks", store.count())


if __name__ == "__main__":
    main()