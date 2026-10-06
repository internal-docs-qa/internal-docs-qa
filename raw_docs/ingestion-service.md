# Ingestion Service


## Overview (part 1)

The ingestion service reads documents from a watched directory and prepares them for retrieval. It runs on a schedule and on demand. The ingestion service reads documents from a watched directory and prepares them for retrieval. It runs on a schedule and on demand.


## Supported formats (part 1)

Markdown is the only supported input format. Files with other extensions are logged and skipped rather than failing the run. Markdown is the only supported input format. Files with other extensions are logged and skipped rather than failing the run.


## Chunking strategy (part 1)

Documents are split on paragraph boundaries wherever possible, so that each chunk contains whole thoughts rather than fragments. Documents are split on paragraph boundaries wherever possible, so that each chunk contains whole thoughts rather than fragments.


## Overlap (part 1)

Consecutive chunks share a short tail of text. This prevents a sentence spanning a boundary from being lost to both chunks. Consecutive chunks share a short tail of text. This prevents a sentence spanning a boundary from being lost to both chunks.


## Metadata (part 1)

Each chunk carries the filename and path of the document it came from, so that answers can cite their source. Each chunk carries the filename and path of the document it came from, so that answers can cite their source.


## Embeddings (part 1)

Chunks are converted to vectors before storage. The same model must be used for documents and for queries. Chunks are converted to vectors before storage. The same model must be used for documents and for queries.


## Storage (part 1)

Vectors are upserted into a collection alongside their metadata. Re-ingesting a document replaces its existing chunks. Vectors are upserted into a collection alongside their metadata. Re-ingesting a document replaces its existing chunks.


## Failure handling (part 1)

A single unreadable file does not stop the run. Errors are logged with the path and the underlying reason. A single unreadable file does not stop the run. Errors are logged with the path and the underlying reason.


## Overview (part 2)

The ingestion service reads documents from a watched directory and prepares them for retrieval. It runs on a schedule and on demand. The ingestion service reads documents from a watched directory and prepares them for retrieval. It runs on a schedule and on demand.


## Supported formats (part 2)

Markdown is the only supported input format. Files with other extensions are logged and skipped rather than failing the run. Markdown is the only supported input format. Files with other extensions are logged and skipped rather than failing the run.


## Chunking strategy (part 2)

Documents are split on paragraph boundaries wherever possible, so that each chunk contains whole thoughts rather than fragments. Documents are split on paragraph boundaries wherever possible, so that each chunk contains whole thoughts rather than fragments.


## Overlap (part 2)

Consecutive chunks share a short tail of text. This prevents a sentence spanning a boundary from being lost to both chunks. Consecutive chunks share a short tail of text. This prevents a sentence spanning a boundary from being lost to both chunks.


## Metadata (part 2)

Each chunk carries the filename and path of the document it came from, so that answers can cite their source. Each chunk carries the filename and path of the document it came from, so that answers can cite their source.


## Embeddings (part 2)

Chunks are converted to vectors before storage. The same model must be used for documents and for queries. Chunks are converted to vectors before storage. The same model must be used for documents and for queries.


## Storage (part 2)

Vectors are upserted into a collection alongside their metadata. Re-ingesting a document replaces its existing chunks. Vectors are upserted into a collection alongside their metadata. Re-ingesting a document replaces its existing chunks.


## Failure handling (part 2)

A single unreadable file does not stop the run. Errors are logged with the path and the underlying reason. A single unreadable file does not stop the run. Errors are logged with the path and the underlying reason.


## Overview (part 3)

The ingestion service reads documents from a watched directory and prepares them for retrieval. It runs on a schedule and on demand. The ingestion service reads documents from a watched directory and prepares them for retrieval. It runs on a schedule and on demand.


## Supported formats (part 3)

Markdown is the only supported input format. Files with other extensions are logged and skipped rather than failing the run. Markdown is the only supported input format. Files with other extensions are logged and skipped rather than failing the run.


## Chunking strategy (part 3)

Documents are split on paragraph boundaries wherever possible, so that each chunk contains whole thoughts rather than fragments. Documents are split on paragraph boundaries wherever possible, so that each chunk contains whole thoughts rather than fragments.


## Overlap (part 3)

Consecutive chunks share a short tail of text. This prevents a sentence spanning a boundary from being lost to both chunks. Consecutive chunks share a short tail of text. This prevents a sentence spanning a boundary from being lost to both chunks.


## Metadata (part 3)

Each chunk carries the filename and path of the document it came from, so that answers can cite their source. Each chunk carries the filename and path of the document it came from, so that answers can cite their source.


## Embeddings (part 3)

Chunks are converted to vectors before storage. The same model must be used for documents and for queries. Chunks are converted to vectors before storage. The same model must be used for documents and for queries.


## Storage (part 3)

Vectors are upserted into a collection alongside their metadata. Re-ingesting a document replaces its existing chunks. Vectors are upserted into a collection alongside their metadata. Re-ingesting a document replaces its existing chunks.


## Failure handling (part 3)

A single unreadable file does not stop the run. Errors are logged with the path and the underlying reason. A single unreadable file does not stop the run. Errors are logged with the path and the underlying reason.
