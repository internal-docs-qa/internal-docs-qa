"""Manual check for US-301: the tool runs, and its schema looks right."""

import logging

from core.embedder import Embedder
from services.vector_store import VectorStore
from tools.search_docs import SearchDocsTool

logging.basicConfig(level=logging.INFO)
for noisy in (
    "httpx",
    "httpcore",
    "sentence_transformers",
    "transformers",
    "huggingface_hub",
    "chromadb",
):
    logging.getLogger(noisy).setLevel(logging.WARNING)

QUERIES = [
    "retry logic",
    "how long do auth tokens last",
    "what is our holiday policy",
    "how do I centre a div in CSS",
]


def main() -> None:
    tool = SearchDocsTool(embedder=Embedder(), store=VectorStore())

    print("=" * 70)
    print("AC 2 - SCHEMA")
    print("=" * 70)
    print(f"name:        {tool.declaration.name}")
    print(f"description: {tool.declaration.description}")
    print()
    print("parameters:")
    print(tool.declaration.parameters)

    print()
    print("=" * 70)
    print("AC 1 - EXECUTION")
    print("=" * 70)
    for query in QUERIES:
        print(f"\n{'-' * 70}")
        print(f"query: {query!r}")
        print(f"{'-' * 70}")
        print(tool.search(query))


if __name__ == "__main__":
    main()
