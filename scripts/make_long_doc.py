"""Generate a long markdown document for testing chunk splitting."""

from pathlib import Path

SECTIONS = [
    ("Overview", "The ingestion service reads documents from a watched directory and "
     "prepares them for retrieval. It runs on a schedule and on demand."),
    ("Supported formats", "Markdown is the only supported input format. Files with "
     "other extensions are logged and skipped rather than failing the run."),
    ("Chunking strategy", "Documents are split on paragraph boundaries wherever "
     "possible, so that each chunk contains whole thoughts rather than fragments."),
    ("Overlap", "Consecutive chunks share a short tail of text. This prevents a "
     "sentence spanning a boundary from being lost to both chunks."),
    ("Metadata", "Each chunk carries the filename and path of the document it came "
     "from, so that answers can cite their source."),
    ("Embeddings", "Chunks are converted to vectors before storage. The same model "
     "must be used for documents and for queries."),
    ("Storage", "Vectors are upserted into a collection alongside their metadata. "
     "Re-ingesting a document replaces its existing chunks."),
    ("Failure handling", "A single unreadable file does not stop the run. Errors are "
     "logged with the path and the underlying reason."),
]

lines = ["# Ingestion Service\n"]

for repeat in range(1, 4):
    for title, body in SECTIONS:
        lines.append(f"\n## {title} (part {repeat})\n")
        lines.append(f"{body} {body}\n")

Path("raw_docs/ingestion-service.md").write_text("\n".join(lines), encoding="utf-8")
print("written")