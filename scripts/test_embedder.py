"""Check the embedder produces vectors."""

from core.embedder import Embedder


def main() -> None:
    embedder = Embedder()

    print(f"model:      {embedder.model_name}")
    print(f"dimensions: {embedder.dimensions()}")
    print(f"max tokens: {embedder.max_tokens}")

    texts = [
        "How do I authenticate with the API?",
        "Tokens are issued by the identity service and expire after 60 minutes.",
        "Roll back immediately if error rates exceed 2%.",
    ]

    vectors = embedder.embed(texts)

    print(f"\n{len(vectors)} vectors, each {len(vectors[0])} numbers")
    print(f"first 5 of vector 0: {vectors[0][:5]}")


if __name__ == "__main__":
    main()