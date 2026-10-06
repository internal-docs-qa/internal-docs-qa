"""Check chunking against the US-103 acceptance criteria."""

import logging

from core.chunker import TextChunker
from core.parser import DocumentParser


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    parser = DocumentParser()
    chunker = TextChunker()

    documents = parser.parse_directory("raw_docs")

    for document in documents:
        chunks = chunker.chunk_document(document)
        total = chunker.count_tokens(document.text)

        print(f"\n=== {document.filename} — {total} tokens → {len(chunks)} chunks ===")

        for chunk in chunks:
            tokens = chunker.count_tokens(chunk.text)
            print(f"\n[{chunk.chunk_index}] {tokens} tokens | {chunk.filename} | {chunk.path}")
            print(chunk.text[:150].replace("\n", " "))

        for i in range(len(chunks)-1):
            tail=chunks[i].text[-100]
            print(f"overlap{i}->{i+1}: {'yes' if tail in chunks[i+1].text else 'no'}")


if __name__ == "__main__":
    main()