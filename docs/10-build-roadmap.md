# Build Roadmap

## Build Philosophy

Build the smallest real system that proves the platform:

```text
import -> model -> embed -> analyze -> explain -> expose through MCP
```

Do not start with every connector. Start with the universal model and one or
two strong demos.

## Phase 0: Foundation Planning

Deliverables:

- architecture docs
- data model docs
- API/MCP draft
- repository structure
- license decision
- stack decision
- local development plan

Exit criteria:

- developer can understand what to build
- MVP scope is clear
- first use cases are selected

## Phase 1: Local Skeleton

Goal:

Start the system locally.

Deliverables:

- monorepo structure
- Docker Compose
- Postgres + pgvector
- Redis
- MinIO
- Qdrant
- API service
- worker service
- scheduler service
- MCP server process
- basic web app shell
- database migrations
- idempotent local seed
- bundled Site Audit module installation
- config system
- logging

Suggested stack:

- Python 3.11+
- FastAPI
- SQLAlchemy or SQLModel
- Alembic
- Celery
- Redis
- Postgres
- Next.js
- TypeScript

Detailed language guidance:
[Language And Runtime Strategy](21-language-and-runtime-strategy.md).

Exit criteria:

```bash
docker compose up
curl http://localhost:8000/health
open http://localhost:3000
```

## Phase 2: Entity Model And Import

Goal:

Import simple data into the universal model.

Deliverables:

- tenants/workspaces/datasets
- modules/module_installations/module_resources
- raw object metadata
- data streams
- source events
- label definitions
- labels and classification on core records
- entity types
- entities
- content units
- content chunks
- metric definitions
- metric values
- CSV/JSONL importer
- website importer basic version
- Site Audit entity/metric/relation definitions

Exit criteria:

```bash
meaninggrid import csv examples/company-benchmark/companies.csv
meaninggrid import website https://example.com --max-pages 100
```

## Phase 3: Embeddings And Vector Store

Goal:

Generate and search embeddings.

Deliverables:

- embedding provider interface
- local sentence-transformers provider
- OpenAI provider optional
- pgvector adapter
- Qdrant adapter
- embedding metadata table
- batch embedding worker
- semantic search API

Exit criteria:

```bash
meaninggrid embed ds_123
meaninggrid search ds_123 "pricing objections"
```

## Phase 4: Analysis Engine MVP

Goal:

Generate useful semantic analysis artifacts.

Deliverables:

- centroid metrics
- pairwise sample stats
- cluster detection
- cluster labeling
- outlier detection
- near-duplicate detection
- 2D projection
- analysis run records
- artifact storage

Exit criteria:

```bash
meaninggrid analyze ds_123
```

produces:

- dataset metrics
- clusters
- outliers
- duplicates
- projection

## Phase 5: Context Layer And MCP MVP

Goal:

Let AI agents discover and query the dataset.

Deliverables:

- dataset card builder
- schema card builder
- context pack builder
- MCP server
- MCP resources
- MCP tools
- MCP prompts
- permission-aware retrieval baseline

Exit criteria:

An MCP client can ask:

- list datasets
- get dataset card
- search context
- build context pack
- get insight evidence

## Phase 6: Web UI MVP

Goal:

Make it usable by humans.

Deliverables:

- dataset catalog
- import status
- entity browser
- semantic map
- cluster table
- outlier table
- duplicate table
- basic insight view
- evidence viewer
- MCP setup page

Exit criteria:

A user can import a website or CSV, run analysis, inspect clusters/outliers,
and copy MCP connection instructions.

## Phase 7: Cohort Comparison

Goal:

Add the highest-value business analysis.

Deliverables:

- cohort builder
- metric filters
- top/bottom metric cohorts
- centroid comparison
- cluster enrichment
- representative evidence
- success pattern insights

Exit criteria:

User can compare:

- successful vs failed calls
- top vs weak branches
- high vs low converting pages

## Phase 8: First Polished Demos

Goal:

Make the open-source project compelling.

Demos:

1. Site Audit/GEO audit
2. Company benchmark from CSV
3. Sales-call transcripts
4. Support-ticket JSONL
5. MCP agent context demo

Each demo should include:

- sample data or import instructions
- commands
- screenshots
- expected outputs
- short video/gif later

## Phase 8b: Module Framework

Goal:

Make specialized domains installable as modules instead of hardcoded forks.

Deliverables:

- module manifest format
- module registry
- module label/filter presets
- module installation records
- bundled Site Audit module
- schema registration
- analysis preset registration
- context-pack template registration
- MCP prompt registration
- dashboard/report registration hooks
- first Marketing module
- first VC module
- first Product Event module

Exit criteria:

- a module can be installed into a workspace
- module schemas appear in dataset creation
- module prompts appear through MCP
- module analysis presets can be run through API/CLI
- Marketing, VC, and Product Event demos use module definitions

## Phase 9: Enterprise Foundations

Goal:

Prepare for serious deployments.

Deliverables:

- OIDC auth
- API tokens
- RBAC
- audit logs
- PII redaction baseline
- object storage abstraction
- Qdrant production config
- Helm chart
- backup/restore docs
- deployment guide

## Phase 9b: Streaming And Reprocessing

Goal:

Support continuously changing datasets and historical reprocessing.

Deliverables:

- data_streams table
- source_events table
- entity_change_events table
- idempotent writes
- periodic sync scheduler
- webhook ingestion endpoint
- backfill jobs
- derivation specs
- derived artifact invalidation
- reprocessing jobs
- recent changes API

## Phase 9c: Push, Labeling, And Filtering

Goal:

Make external systems and agents able to push richly labeled data and retrieve
it later through consistent filters.

Deliverables:

- JSONL push
- JSON batch push
- document push
- metric push
- relation push
- canonical push envelope
- label definitions
- label propagation
- classification fields
- idempotency support
- filter grammar
- vector payload labels
- MCP/API filter support

Exit criteria:

- user can push labeled JSONL data
- user can upload labeled documents
- vector search can filter by labels and classification
- MCP tools accept canonical filters
- analysis runs can be scoped by filters

Exit criteria:

- a connector can periodically push new metrics
- duplicate events are ignored safely
- changed content triggers re-embedding
- changed metrics trigger incremental analysis
- historical raw data can be reprocessed with a new metric extractor

## Phase 9d: Streaming Agent Context Engine

Goal:

Let long-running AI agents subscribe to meaningful context changes without
reading internal event streams.

Deliverables:

- canonical streaming event envelope fields
- event_routes table
- deterministic route rules
- context_units table
- first context unit builders
- agent_subscriptions table
- context_notifications table
- notify-then-pull MCP resources
- notification ack and resume
- routing feedback tool
- shared memory table

Exit criteria:

- an agent can subscribe to a filtered context stream
- urgent events create notifications with stable sequence IDs
- agent can pull a context unit and acknowledge the notification
- duplicate notifications can be deduplicated
- routing feedback is stored for future classifier improvement

## Phase 10: Managed Infrastructure

Goal:

Build SaaS/private-deployment business.

Deliverables:

- multi-tenant SaaS deployment
- billing/usage metering
- tenant-specific vector isolation options
- admin console
- monitoring
- support tooling
- enterprise onboarding docs
- managed headless deployments

## MVP Scope

The first public MVP should include:

- Docker Compose
- API
- worker
- Postgres + pgvector
- optional Qdrant
- local embeddings
- CSV/JSONL importer
- website crawler
- semantic analysis
- context packs
- MCP server
- headless profile
- basic web UI

Leave out of MVP:

- many SaaS admin features
- advanced billing
- all premium connectors
- complex ABAC
- multi-region
- sophisticated report builder

## Suggested Team Sequencing

Solo/founder build order:

1. data model and migrations
2. CLI import path
3. embedding pipeline
4. analysis engine
5. MCP server
6. minimal UI
7. demos and docs
8. module framework
9. first specialized modules
10. streaming agent context subscriptions

Two-person build:

- Person A: backend, data model, workers, analysis
- Person B: frontend, import UI, visualizations, docs

Three-person build:

- Backend/infra
- Analysis/ML
- Frontend/product

## Quality Gates

Each phase should include:

- unit tests for pure logic
- integration tests for import/analyze
- fixture datasets
- migration tests
- basic security tests
- manual demo script

Important test fixtures:

- tiny website
- duplicate pages
- outlier page
- company CSV with success metric
- calls JSONL with won/lost outcome
- support tickets with repeated themes
- marketing dataset with keyword/content gaps
- VC dataset with invested and rejected companies
