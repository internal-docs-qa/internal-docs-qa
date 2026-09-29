"""Quick check that the parser reads raw_docs correctly."""

from core.parser import DocumentParser


def main() -> None:
    parser = DocumentParser()
    documents = parser.parse_directory("raw_docs")

    print(f"Found {len(documents)} documents\n")

    for document in documents:
        print(f"--- {document.filename} ---")
        print(f"path: {document.path}")
        print(f"length: {len(document.text)} characters")
        print(document.text[:600])
        print()


if __name__ == "__main__":
    main()