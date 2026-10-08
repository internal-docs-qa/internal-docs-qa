"""Query the vector store and print the most relevant chunks."""

import logging
import sys

from core.embedder import Embedder
from services.vector_store import VectorStore


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    for noisy in ("httpx", "httpcore", "sentence_transformers", "transformers", "huggingface_hub"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    question = " ".join(sys.argv[1:]) or "authentication"

    embedder = Embedder()
    store = VectorStore()

    vector = embedder.embed([question])[0]
    results = store.query(vector, top_k=3)

    print(f'\nQuery: "{question}"  ({store.count()} chunks in collection)\n')

    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        print(f"--- {rank}. {metadata['filename']} #{metadata['chunk_index']} "
              f"(distance {result['distance']:.4f}) ---")
        print(f"{str(result['text'])[:300]}\n")


if __name__ == "__main__":
    main()