# Language And Runtime Strategy

## Principle

MeaningGrid should start with a small language footprint.

Recommended MVP languages:

```text
Python
TypeScript
SQL
YAML/JSON
Shell
```

Avoid adding Go, Rust, Java, Scala, or JVM streaming frameworks until there is a
clear performance, packaging, or enterprise-integration reason.

The first product is complex because of the domain model, not because it needs
many programming languages. Keeping the core in fewer languages will make the
open-source project easier to understand, debug, and extend.

## Default Recommendation

```text
Backend/API/workers/analysis/connectors: Python
Web UI: TypeScript
Database: SQL + Alembic migrations
Modules: YAML/JSON manifests + Python extension functions
Infrastructure: Docker Compose YAML, later Helm/Terraform
```

This is the best fit because:

- semantic analysis, embeddings, clustering, extraction, and data processing
  are Python-heavy
- the UI ecosystem is strongest in TypeScript/React
- module definitions should be declarative where possible
- local Docker should be simple and contributor-friendly
- the system can later expose SDKs in more languages without rewriting core

## Component Language Matrix

| System Part | MVP Language | Recommended Tools | Why |
|---|---|---|---|
| Web UI | TypeScript | Next.js, React, TanStack Query, Tailwind or restrained component system | Best ecosystem for dashboards, maps, tables, and interactive workflows |
| API service | Python | FastAPI, Pydantic, SQLAlchemy/SQLModel, Alembic | Close to analysis code, fast development, strong typed API contracts |
| Worker service | Python | Celery + Redis first, Temporal later | Same packages as API and analysis; easy local Docker |
| Scheduler | Python | Celery Beat, APScheduler, or Temporal schedules later | Runs syncs, recrawls, backfills, monitors |
| MCP server | Python first | Thin MCP adapter over context package and API | Shares permission, context, and retrieval logic with backend |
| CLI | Python | Typer, Rich, httpx | Reuses SDK and backend models; good developer UX |
| Connectors | Python | httpx, pydantic, tenacity, requests-oauthlib | API integrations, retries, normalization, source events |
| Website crawler | Python | httpx, Playwright Python, selectolax/lxml, trafilatura | Keeps crawler in worker runtime; handles static and rendered pages |
| Content extraction | Python | selectolax, lxml, BeautifulSoup, trafilatura, readability | Strong text extraction and HTML tooling |
| Analysis engine | Python | numpy, scipy, scikit-learn, polars/pandas, umap-learn, hdbscan | Natural home for clustering, vectors, metrics, projections |
| Embeddings | Python | sentence-transformers, provider adapters | Local and hosted embedding support |
| Vector store adapters | Python | qdrant-client, psycopg/pgvector | Direct backend integration |
| Streaming context engine | Python first | Redis Streams/Celery, later Temporal or Kafka adapters | Shares event model and route logic; replace only if throughput demands it |
| Reports | Python + TypeScript | Jinja/HTML backend, React previews, Playwright PDF later | Backend reproducibility plus UI preview |
| Module manifests | YAML/JSON | JSON Schema validation | Declarative, reviewable, versionable |
| Module custom logic | Python | Plugin registry, entrypoints, sandbox later | Analysis/connectors need backend libraries |
| Module UI extensions | TypeScript later | React components or dashboard schema | Only when declarative dashboards are not enough |
| Database schema | SQL + Python migrations | Alembic, SQLAlchemy metadata | Explicit migrations and stable schema history |
| Analytics queries | SQL | Postgres SQL, ClickHouse SQL | Best for metrics, time windows, rollups |
| Infrastructure | YAML/HCL/Shell | Docker Compose, Helm, Terraform, Make/just | Standard deployment tooling |
| Tests | Python + TypeScript | pytest, Vitest, Playwright | Match runtime languages |
| SDKs | Python + TypeScript | OpenAPI-generated clients plus hand-written helpers | Covers backend automation and web/agent ecosystem |

## Backend: Python

Use Python for:

- API
- workers
- scheduler
- CLI
- connectors
- crawler
- analysis engine
- embedding pipeline
- vector store adapters
- context pack builder
- streaming context engine MVP
- report generation

Recommended baseline:

```text
Python 3.12 or 3.11+
FastAPI
Pydantic v2
SQLAlchemy 2.x or SQLModel
Alembic
Celery + Redis
pytest
ruff
uv
```

Why Python:

- strongest ecosystem for NLP, embeddings, clustering, and extraction
- lower friction for analysis-heavy contributors
- avoids service boundaries between API and analysis in the MVP
- easy to package in Docker
- good enough performance for initial local and self-hosted workloads

Guideline:

Keep core business logic in Python packages, not inside FastAPI route handlers.
Routes should validate input, call services, and return typed responses.

## Web UI: TypeScript

Use TypeScript for:

- web app
- dashboard views
- semantic maps
- report previews
- dataset setup wizards
- module-driven UI forms
- generated API client

Recommended baseline:

```text
TypeScript
Next.js
React
TanStack Query
TanStack Table
Tailwind or a restrained component system
Plot/D3 for charts
Playwright for UI tests
```

Why TypeScript:

- best frontend ecosystem
- type safety for API contracts
- strong table/chart/map tooling
- good contributor familiarity

Guideline:

Do not put core analysis logic in the browser. The UI should visualize and
operate on API artifacts.

## MCP Server: Python First, Thin Adapter

The MCP server should start in Python because:

- context-pack building will be Python
- permissions and filters will be Python
- semantic retrieval adapters will be Python
- fewer cross-language calls in MVP

But the MCP protocol layer should stay thin:

```text
MCP request -> auth/session -> context service -> response
```

If the TypeScript MCP ecosystem becomes clearly better for server
implementation, a TypeScript MCP server can later call the same API endpoints.
This should not require rewriting context logic.

## CLI: Python First

Use Python with Typer/Rich.

Commands:

```text
meaninggrid init
meaninggrid serve
meaninggrid import website
meaninggrid import csv
meaninggrid push jsonl
meaninggrid analyze
meaninggrid search
meaninggrid context-pack
meaninggrid module install
meaninggrid backup create
```

Later, a Go or Rust CLI can be considered if:

- single binary distribution becomes important
- startup time matters
- installation with Python is too painful for non-developers

For the open-source MVP, Python CLI is faster and simpler.

## Modules: Mostly Declarative

Modules should not require writing code for common cases.

Use YAML/JSON for:

- module manifest
- entity types
- relation definitions
- metric definitions
- label definitions
- connector configuration
- mapping presets
- analysis presets
- context pack templates
- context unit templates
- dashboards
- report templates
- MCP prompt registration
- monitor templates

Use Python only for:

- custom connector logic
- custom extraction logic
- custom metric computation
- custom analysis algorithms
- custom context unit builders
- custom report generation

Use TypeScript only for:

- custom UI components
- advanced visualizations
- dashboard widgets that cannot be expressed declaratively

This keeps paid and community modules easier to inspect and install.

## Data And Schema Languages

Use SQL for:

- schema migrations
- views
- materialized views
- report queries
- ClickHouse analytics

Use JSON Schema for:

- module manifest validation
- connector config validation
- mapping preset validation
- analysis preset validation
- API payload contracts where useful

Use YAML for human-authored configuration. Convert YAML to validated JSON
internally.

## Streaming And High-Volume Processing

MVP:

```text
Python + Redis Streams/Celery
```

Enterprise later:

```text
Python adapters over Kafka/Redpanda/NATS
ClickHouse SQL for analytics rollups
Flink SQL or Java/Kotlin only if customers need true stream processing at scale
```

Do not start with Scala/Java/Flink unless:

- event volumes exceed what Python workers can handle
- customers already run Flink
- windowed stream processing becomes central
- exactly-once-like stream/table semantics become required

The architecture should allow Flink later, but the first implementation should
not depend on it.

## Performance Escape Hatches

Add a new language only when there is a measured reason.

### Go

Good later for:

- high-throughput API gateway
- standalone CLI binary
- lightweight connector runner
- agent gateway
- event router

Do not use in MVP unless the team is already Go-heavy.

### Rust

Good later for:

- very fast HTML parsing
- vector/math hot paths
- secure plugin sandboxing
- single-binary local appliance pieces
- WASM module runtime

Do not use in MVP unless a specific bottleneck is proven.

### Java/Kotlin/Scala

Good later for:

- Apache Flink jobs
- Kafka Streams
- enterprise streaming integrations

Avoid in MVP. JVM stream processing is powerful but increases contributor and
ops complexity.

## Repository Layout By Language

```text
apps/
  api/                  Python
  worker/               Python
  scheduler/            Python
  mcp-server/           Python
  web/                  TypeScript
  cli/                  Python

packages/
  core/                 Python
  db/                   Python + SQL migrations
  connectors/           Python
  ingestion/            Python
  analysis/             Python
  context/              Python
  streaming-context/    Python
  embeddings/           Python
  vectorstores/         Python
  objectstore/          Python
  reports/              Python
  security/             Python
  sdk-python/           Python
  sdk-ts/               TypeScript

modules/
  site-audit/           YAML + Python + Markdown prompts
  marketing/            YAML + Python + Markdown prompts
  vc/                   YAML + Python + Markdown prompts

deployments/
  docker-compose/       YAML
  helm/                 YAML/templates
  terraform/            HCL
```

## API Contracts Between Languages

Use OpenAPI as the contract between Python backend and TypeScript frontend.

Rules:

- API responses should be typed Pydantic models.
- Generate TypeScript client from OpenAPI.
- Do not hand-maintain duplicate TS types for API payloads.
- Keep filter grammar and module schemas JSON-serializable.
- Keep MCP responses aligned with the same context contracts where possible.

## Coding Standards

Python:

```text
ruff
pyright or mypy later
pytest
Pydantic models at boundaries
SQLAlchemy/Alembic for persistence
```

TypeScript:

```text
eslint
prettier
tsconfig strict
vitest
playwright
generated API client
```

SQL:

```text
explicit migrations
stable naming conventions
foreign keys for core tables
GIN indexes for JSONB only when needed
```

YAML/JSON:

```text
JSON Schema validation
version fields
module compatibility constraints
clear error messages
```

## First Implementation Choice

Build the first version with:

```text
Python backend monolith + workers
TypeScript web app
Postgres SQL migrations
YAML module definitions
Docker Compose local runtime
```

This is enough to ship:

- local Docker appliance
- Site Audit/GEO module
- crawler
- embeddings
- semantic analysis
- UI
- MCP server
- report generation

Then add more languages only when the product earns the complexity.
