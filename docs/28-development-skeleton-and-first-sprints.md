# Development Skeleton And First Sprints

## Purpose

This document turns the v0 specs into an implementation sequence.

The first engineering goal is a working local skeleton, then a thin vertical
slice of Site Audit.

Concrete choices are locked in:
[Engineering Decisions V0](29-engineering-decisions-v0.md).

## Repository Skeleton

```text
apps/
  api/
  worker/
  scheduler/
  mcp-server/
  web/
  cli/
packages/
  core/
  db/
  connectors/
  ingestion/
  analysis/
  context/
  embeddings/
  vectorstores/
  objectstore/
  reports/
  security/
modules/
  site-audit/
deployments/
  docker-compose/
migrations/
examples/
  site-audit/
docs/
```

## Tooling

Python:

```text
uv
ruff
pytest
FastAPI
Pydantic
SQLAlchemy
Alembic
Celery
Typer
```

TypeScript:

```text
pnpm
Next.js
React
TanStack Query
TanStack Table
Vitest
Playwright
```

Root commands:

```bash
make setup
make dev
make test
make lint
make format
make migrate
make seed
```

Using `just` instead of `make` is also acceptable. Pick one.

## First Docker Compose

Services:

```text
postgres
redis
minio
qdrant
api
worker
scheduler
mcp-server
web
```

Health checks:

- Postgres accepts connections.
- API `/health` returns ok.
- Web returns 200.
- Worker can connect to Redis.
- API can connect to Qdrant and MinIO.

## Sprint 1: Local Skeleton

Goal:

```text
docker compose up --build gives a working empty app
```

Tasks:

- create monorepo folders
- add Python workspace/package config
- add TypeScript web app
- add Dockerfiles
- add Docker Compose
- add Postgres/Redis/MinIO/Qdrant services
- add FastAPI health endpoint
- add Celery worker
- add Alembic setup
- add first migrations for identity/workspace/module/dataset
- add seed command
- add basic web app shell
- add generated or hand-written temporary API client

Demo:

```bash
docker compose up --build
curl http://localhost:8000/health
open http://localhost:3000
```

Done when:

- local app starts from clean clone
- database has local tenant/workspace/user
- Site Audit module record exists
- web app shows dataset list empty state

Current implementation status:

- Docker Compose includes a `migrate` service for Alembic plus local seed.
- The first migration creates identity, workspace, module, dataset, source,
  schema registry, and job tables.
- The API reads workspaces/modules from Postgres and can create datasets and
  queued Site Audit jobs.
- Integration tests cover local seed idempotency, workspace/module reads,
  dataset creation, crawl job enqueueing, job events, cancellation, and API
  error shape.

## Sprint 2: Core Model And Dataset Creation

Goal:

```text
create a Site Audit dataset from UI/API
```

Tasks:

- implement datasets API
- implement modules API
- implement schema registry tables
- seed Site Audit entity types/metrics/relations
- implement jobs table
- implement job status API
- implement New Site Audit wizard UI
- create source and data stream for website crawler

Demo:

```text
open UI -> New Site Audit -> create dataset -> see dataset detail
```

Done when:

- dataset exists in database
- source exists
- module resources are visible
- UI can show dataset detail

## Sprint 3: Website Crawl And Extraction

Goal:

```text
crawl a small fixture website and create page/content/link records
```

Tasks:

- implement URL normalization
- implement sitemap discovery
- implement robots handling baseline
- implement page fetcher
- store raw HTML in MinIO
- create raw_objects and source_events
- extract title/meta/canonical/headings/paragraphs/links
- create domain/crawl_run/page entities
- create content_units and content_chunks
- create entity_relations for internal links
- create technical metric_values
- show crawl progress in UI

Demo:

```text
start fixture crawl -> pages table appears with extracted pages
```

Done when:

- 5-page fixture crawls successfully
- page detail shows extracted content
- broken link is recorded
- missing title/meta metrics are present

## Sprint 4: Embeddings And Semantic Search

Goal:

```text
embed page content and search semantically
```

Tasks:

- implement embedding model registry
- implement local embedding provider
- implement Qdrant adapter
- implement pgvector adapter or postpone to Sprint 5 if Qdrant is primary
- implement embedding run job
- write vector payload metadata
- implement semantic search API
- add search UI
- add MCP semantic_search tool baseline

Demo:

```text
search "pricing workflow" -> relevant page chunks return
```

Done when:

- chunks embed
- re-run skips unchanged chunks
- semantic search returns evidence snippets

## Sprint 5: Site Audit Analysis V0

Goal:

```text
produce technical, semantic, and basic GEO analysis artifacts
```

Tasks:

- implement technical issue rules
- implement technical score
- implement page similarity
- implement duplicate detection
- implement cluster generation
- implement centroid distance outliers
- implement internal link opportunities
- implement GEO readiness score
- write analysis_artifacts
- write insights and evidence
- show overview/issues/outliers/duplicates/GEO UI

Demo:

```text
run analysis -> overview shows issues, clusters, outliers, duplicates, GEO score
```

Done when:

- fixture expected issues are detected
- insight evidence resolves
- UI displays analysis artifacts

## Sprint 6: Context, Reports, MCP

Goal:

```text
agent and human can consume the audit
```

Tasks:

- implement dataset card builder
- implement context pack builder for Site Audit
- implement report HTML generation
- add report viewer
- implement MCP server resources/tools
- add MCP setup page
- add CLI commands for import/analyze/search

Demo:

```text
MCP client asks for biggest GEO weaknesses and receives evidence-backed context
```

Done when:

- context pack can be built
- report renders
- MCP list/search/evidence tools work
- CLI can start a crawl/analyze flow

## First Release Cut

Release v0.1 when:

- all Sprint 1-6 demos pass
- Docker fresh-start test passes
- fixture integration tests pass
- README has local setup instructions
- Site Audit docs match implementation
- known limitations are documented

## Branching And Commits

Simple early rule:

```text
main stays working
feature branches for larger changes
small commits with clear messages
```

No complicated release process yet.

## CI V0

GitHub Actions:

- Python lint/test
- TypeScript lint/test
- build Docker images if feasible
- run migration test

Later:

- full Docker Compose integration test
- Playwright test
- MCP smoke test

## Implementation Risks

### Crawler Complexity

Risk:

Web crawling becomes a product by itself.

Mitigation:

- support static HTML first
- cap page count
- keep Playwright optional
- log failures instead of perfecting all edge cases

### Analysis Overreach

Risk:

GEO scoring becomes subjective and vague.

Mitigation:

- use transparent formulas
- show component scores
- show evidence
- label as v0 heuristic

### Schema Overengineering

Risk:

Trying to build every future table before the first crawl works.

Mitigation:

- implement v0 tables only
- preserve extension points
- add streaming-agent tables later

### UI Overbuild

Risk:

Building dashboard framework instead of Site Audit workflow.

Mitigation:

- hardcode Site Audit v0 views first
- use module metadata only where simple
- generalize after the workflow proves itself
