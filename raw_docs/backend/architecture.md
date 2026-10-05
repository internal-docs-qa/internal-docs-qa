# Backend Architecture

## Service layout

The backend is split into four layers. The API layer handles HTTP
requests and responses. The core layer holds business logic and is
independent of transport. The services layer wraps external systems
such as the vector store and the LLM provider. The data layer holds
models and persistence helpers.

## Dependency direction

Dependencies point inward. The API layer may call core and services.
Core must not import from the API layer, so the same logic can be
driven by a CLI command or a scheduled job.

## Vector store

ChromaDB runs as a container and is reached over HTTP on port 8000.
Embeddings are generated before insertion, never inside the database.
Collection names follow the pattern <project>\_<environment>.

<div class="warning">Do not query the collection directly from the
API layer. Route all access through the retrieval service.</div>

## Decisions

Architecture decisions are recorded as ADRs in docs/adr. Each ADR
states the context, the decision, and the consequences. Superseded
ADRs are kept rather than deleted.
