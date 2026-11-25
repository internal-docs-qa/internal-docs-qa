"""Ask a question against the real document collection."""

import logging
import sys

from core.embedder import Embedder
from core.prompt_templates import format_context
from services.llm_service import LLMService
from services.vector_store import VectorStore


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    for noisy in ("httpx", "httpx2", "httpcore", "google_genai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    question = " ".join(sys.argv[1:]) or "how long do auth tokens last?"

    embedder = Embedder()
    store = VectorStore()
    llm = LLMService()

    vector = embedder.embed([question])[0]
    matches = store.query(vector, top_k=3)
    context = format_context(matches)
    answer = llm.generate_response(context, question)

    print(f"\nQ: {question}\n")
    print(answer)
    print("\nchunks used:")
    for match in matches:
        print(f"  {match['metadata']['filename']} #{match['metadata']['chunk_index']}")


if __name__ == "__main__":
    main()