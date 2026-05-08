# Engineering Decisions V0

## Purpose

This document locks the concrete engineering choices needed to start building
MeaningGrid v0.1.

The broader architecture is intentionally larger than v0.1. These decisions
focus only on the first local Site Audit application.

## Decisions

### Package And Task Tools

Decision:

```text
Python package/dependency tool: uv where useful, requirements.txt for first Docker image
Frontend package manager: pnpm
Task runner: make
```

Reason:

- `uv` is fast and works well for local Python development.
- `requirements.txt` keeps the first backend Docker image simple.
- `pnpm` is predictable for a TypeScript workspace.
- `make` is universally available enough for early contributors.

### Backend Framework

Decision:

```text
FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic
```

Reason:

- FastAPI gives OpenAPI and typed request/response models quickly.
- Pydantic v2 gives strict boundary validation.
- SQLAlchemy/Alembic is the safest path for a Postgres-first system.

### Worker Runtime

Decision:

```text
Celery + Redis
```

Reason:

- Simple local Docker setup.
- Good enough for crawl, extraction, embedding, analysis, and report jobs.
- Can be replaced by Temporal later without changing the application model.

### Frontend Framework

Decision:

```text
Next.js + TypeScript + TanStack Query + TanStack Table
```

Reason:

- Strong ecosystem for data-heavy UI.
- Easy local development.
- TypeScript client can be generated from OpenAPI later.

### Styling

Decision:

```text
Start with plain CSS/local components. Add Tailwind after UI shape stabilizes.
```

Reason:

- Keeps first scaffold light.
- Avoids spending early time on design-system plumbing.
- Tailwind can be added without changing product architecture.

### Embedding Model

Decision:

```text
Default local model: sentence-transformers/all-MiniLM-L6-v2
```

Reason:

- Small and fast enough for local machines.
- Good enough for page/paragraph similarity in v0.
- Easy to replace through embedding model registry.

Implementation note:

Keep heavy ML dependencies in `requirements-ml.txt` or a future embedding
worker image. The first backend scaffold should stay light enough to build
quickly.

### Crawler Libraries

Decision:

```text
httpx + selectolax + trafilatura
```

Reason:

- Static HTML first.
- Fast parsing.
- Good main-content extraction fallback.

Later:

```text
Playwright behind render_javascript=true
```

### Database IDs

Decision:

```text
UUID primary keys using Postgres gen_random_uuid() defaults.
```

Reason:

- Works locally and in distributed systems later.
- Good for API exposure.
- Avoids sequence assumptions across tenants/imports.

### Auth V0

Decision:

```text
AUTH_MODE=local
```

Meaning:

- seed one local admin user
- no SaaS auth in v0.1
- all API calls run as local admin unless an explicit local token is added

Reason:

- Faster local development.
- Avoids blocking product work on enterprise auth.
- Tenancy/workspace IDs still exist from the first migration.

### Storage V0

Decision:

```text
Postgres: source of truth
Redis: queue/cache
MinIO: raw objects and artifacts
Qdrant: default vector store
pgvector: enabled for fallback/minimal mode
```

Reason:

- Mirrors future standalone architecture.
- Proves object storage and vector storage early.
- Still runs locally through Docker Compose.

### MCP Server V0

Decision:

```text
Python MCP server as a thin adapter.
```

Reason:

- It can reuse context/search/evidence code.
- Protocol logic stays separate and can move later.

### Fixture Site

Decision:

```text
Create examples/site-audit/fixture-site.
```

Reason:

- Enables deterministic crawler and analysis tests.
- Gives contributors a known local target.

### First Development Target

Decision:

```text
Create runnable skeleton before database implementation.
```

The first scaffold must start:

- API health endpoint
- web shell
- worker process
- scheduler process
- MCP health endpoint
- storage services

Then implement migrations and seed.

## Deferred Decisions

Defer:

- OIDC provider
- paid module packaging/signing
- Temporal
- ClickHouse default profile
- Kafka/Redpanda
- local LLM runtime
- Tailwind/component library
- generated API client
- PDF rendering
- Playwright crawling
- Go/Rust CLI

## Current Build Direction

Build in this order:

1. Repository skeleton.
2. Local Docker Compose.
3. API/web health.
4. Database migrations.
5. Seed local workspace and Site Audit module.
6. Dataset creation.
7. Fixture crawler.
8. Extraction.
9. Embeddings.
10. Site Audit analysis.
