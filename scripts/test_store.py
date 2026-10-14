"""Check that vectors can be stored in and retrieved from ChromaDB."""

import logging

from core.embedder import Embedder
from services.vector_store import VectorStore


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    store = VectorStore(collection_name="smoke_test")
    embedder = Embedder()

    print(f"connected. collection holds {store.count()} chunks")
    if store.count() == 0:
        print("collection is empty, nothing to query yet")
        return

    question = "how do I authenticate?"
    vector = embedder.embed([question])[0]
    results = store.query(vector, top_k=3)

    print(f"query returned {len(results)} results")


if __name__ == "__main__":
    main()