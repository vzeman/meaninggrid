# MeaningGrid

MeaningGrid is an open-source semantic intelligence and context management
platform for AI agents and humans.

It imports messy business data from websites, files, databases, support tools,
call transcripts, CRMs, and custom APIs. It maps that data into entities,
content units, metrics, relations, vectors, and analysis artifacts. It then
helps humans and AI agents find clusters, outliers, gaps, similarities,
success patterns, and recommendations with source evidence.

MeaningGrid should support both static imports and continuously changing data:
periodic syncs, webhooks, event streams, CDC, backfills, and reprocessing of
historical raw data when new metrics or analysis methods are introduced.
For long-running AI agents, it should also support live context subscriptions:
incoming events can update hot context views, produce durable context units,
and notify agents only when something relevant changes.

The long-term company strategy is open-source infrastructure first:

- The community project should be useful locally and in secure environments.
- The default local distribution should include a full Site Audit/GEO workflow.
- Revenue comes from managed infrastructure, private deployments, enterprise
  connectors, support, governance, and scale.
- The web dashboard should be optional; MeaningGrid should also work headlessly
  through MCP, API, and CLI for AI-agent-first workflows.

## Positioning

Short:

> Open-source semantic intelligence and context management for AI agents.

Product definition:

> MeaningGrid helps teams import business data, map it into entities,
> relationships, metrics, and vector spaces, then expose it through dashboards,
> APIs, reports, and MCP so AI agents can progressively discover and understand
> the data with evidence.

Tagline options:

- Map meaning across your business data.
- Find patterns, gaps, and outliers in meaning.
- Turn unstructured data into explainable insights.
- Semantic context infrastructure for AI agents.

## Core Idea

```text
semantic vectors + structured metrics + entity graph + context packs + evidence
```

Product surfaces:

```text
human dashboard + agent MCP interface + infrastructure API
```

The system should answer questions like:

- Which pages dilute topical authority?
- Which companies look similar to successful companies, and where do they differ?
- Which branches underperform, and what patterns explain it?
- Which sales calls fail after pricing is mentioned?
- Which support tickets reveal product gaps?
- Which data should an AI agent read before producing a trustworthy report?

## Planning Documents

Start here:

- [docs/00-index.md](docs/00-index.md)
- [docs/01-product-strategy.md](docs/01-product-strategy.md)
- [docs/02-system-architecture.md](docs/02-system-architecture.md)
- [docs/03-data-model.md](docs/03-data-model.md)
- [docs/04-context-layer-mcp.md](docs/04-context-layer-mcp.md)
- [docs/05-analysis-engine.md](docs/05-analysis-engine.md)
- [docs/06-connectors-ingestion.md](docs/06-connectors-ingestion.md)
- [docs/07-storage-infrastructure.md](docs/07-storage-infrastructure.md)
- [docs/08-security-governance.md](docs/08-security-governance.md)
- [docs/09-open-source-enterprise.md](docs/09-open-source-enterprise.md)
- [docs/10-build-roadmap.md](docs/10-build-roadmap.md)
- [docs/11-api-and-mcp-surface.md](docs/11-api-and-mcp-surface.md)
- [docs/12-decisions-and-open-questions.md](docs/12-decisions-and-open-questions.md)
- [docs/13-use-case-templates.md](docs/13-use-case-templates.md)
- [docs/14-implementation-backlog.md](docs/14-implementation-backlog.md)
- [docs/15-streaming-incremental-data.md](docs/15-streaming-incremental-data.md)
- [docs/16-headless-agent-infrastructure.md](docs/16-headless-agent-infrastructure.md)
- [docs/17-modular-architecture-and-modules.md](docs/17-modular-architecture-and-modules.md)
- [docs/18-data-push-labeling-filtering.md](docs/18-data-push-labeling-filtering.md)
- [docs/19-streaming-agent-context-engine.md](docs/19-streaming-agent-context-engine.md)
- [docs/20-local-docker-infrastructure-and-flexible-schema.md](docs/20-local-docker-infrastructure-and-flexible-schema.md)
- [docs/21-language-and-runtime-strategy.md](docs/21-language-and-runtime-strategy.md)
- [docs/22-mvp-scope-and-acceptance.md](docs/22-mvp-scope-and-acceptance.md)
- [docs/23-initial-database-schema-v0.md](docs/23-initial-database-schema-v0.md)
- [docs/24-site-audit-v0-pipeline-and-analysis.md](docs/24-site-audit-v0-pipeline-and-analysis.md)
- [docs/25-api-contract-v0.md](docs/25-api-contract-v0.md)
- [docs/26-worker-jobs-and-state-machines.md](docs/26-worker-jobs-and-state-machines.md)
- [docs/27-ui-information-architecture-v0.md](docs/27-ui-information-architecture-v0.md)
- [docs/28-development-skeleton-and-first-sprints.md](docs/28-development-skeleton-and-first-sprints.md)
- [docs/29-engineering-decisions-v0.md](docs/29-engineering-decisions-v0.md)
- [docs/modules/README.md](docs/modules/README.md)
- [docs/modules/module-feature-mapping.md](docs/modules/module-feature-mapping.md)

## Development

First local target:

```bash
cp .env.example .env
docker compose up --build
```

The `migrate` service runs Alembic and the idempotent local seed before the API
starts. To run them manually:

```bash
make migrate
make seed
```

Run the current backend integration tests and web typecheck with:

```bash
make test
```

For local development, crawl jobs can be queued through the API and executed
immediately with:

```bash
POST /jobs/{job_id}/run-now
```

Expected local URLs:

- Web UI: http://localhost:3000
- API: http://localhost:8000
- API health: http://localhost:8000/health
- MCP placeholder: http://localhost:8010/health
- Postgres: localhost:15432
- Redis: localhost:16379
- MinIO console: http://localhost:9001
- Qdrant vector store: http://localhost:6333

Qdrant is part of the first implementation, not an optional future service.
The API health endpoint reports `vector_store=ok` when the local Qdrant service
is reachable.

The first implementation slice is documented in:

- [docs/22-mvp-scope-and-acceptance.md](docs/22-mvp-scope-and-acceptance.md)
- [docs/28-development-skeleton-and-first-sprints.md](docs/28-development-skeleton-and-first-sprints.md)
- [docs/29-engineering-decisions-v0.md](docs/29-engineering-decisions-v0.md)
- [docs/30-ddd-architecture-and-quality-standard.md](docs/30-ddd-architecture-and-quality-standard.md)
