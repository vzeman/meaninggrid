# Decisions And Open Questions

## Initial Decisions

### Project Name

Decision:

```text
MeaningGrid
```

Reason:

- clear
- close to MeaningHub
- works for semantic maps and entity grids
- broad enough for websites, companies, calls, tickets, and agents

### Product Direction

Decision:

```text
Open-source semantic intelligence and context management for AI agents.
```

MeaningGrid is not only a dashboard and not only a vector database. The core
platform includes entity modeling, analysis, context packs, and MCP.

### Open Source First

Decision:

Build as an open-source project first. Sell infrastructure and enterprise
deployment later.

### Storage

Decision:

Use Postgres as source of truth. Support pgvector for simple/local vector
search. Support Qdrant as primary scalable vector store. Add ClickHouse for
analytics when needed.

### Architecture

Decision:

Start as a modular monorepo with separate web, API, worker, and MCP server
apps.

### Context Layer

Decision:

Context management is a first-class subsystem. It should support progressive
discovery, context packs, MCP resources, MCP tools, MCP prompts, redaction,
and evidence.

### Streaming And Reprocessing

Decision:

MeaningGrid should support static imports and continuously changing datasets.
New data, changed data, deleted data, periodic syncs, webhooks, streams, CDC,
backfills, and reprocessing should be first-class architecture concepts.

### Streaming Agent Context Engine

Decision:

MeaningGrid should include a streaming-first context engine for long-running
AI agents. Incoming events should be classified into fast, batch,
fast-and-batch, archive-only, or noise paths. Agents should subscribe to
MeaningGrid context resources through MCP/API, not to internal event bus topics.

Initial delivery guarantee:

```text
at-least-once notifications with idempotency and per-partition ordering
```

### Headless Agent Infrastructure

Decision:

MeaningGrid must run as headless infrastructure. The web dashboard is optional;
MCP, API, and CLI are first-class product surfaces. In agent-first deployments,
AI agents become the interface users rely on to understand data.

### Modular Architecture

Decision:

Domain-specific functionality should be implemented as modules over the core,
not as separate forks. Modules register schemas, connectors, analysis presets,
context templates, MCP prompts, dashboards, reports, and monitors.

## Recommended Initial Stack

```text
Frontend: Next.js + TypeScript
API: FastAPI + Python
Workers: Celery + Redis
Database: Postgres
Vectors: pgvector first, Qdrant adapter early
Object storage: local filesystem first, MinIO/S3 adapter next
Analysis: Python packages
MCP server: Python or TypeScript, depending on SDK maturity
Deployment: Docker Compose first
```

Detailed component-by-component language guidance:
[Language And Runtime Strategy](21-language-and-runtime-strategy.md).

## Key Open Questions

### License

Options:

- Apache 2.0
- AGPL 3.0
- dual license

Recommendation:

```text
AGPL-3.0 for server/core, Apache-2.0 for SDKs, commercial license for enterprise.
```

But if maximum adoption is more important than SaaS protection, choose Apache
2.0.

### API Language

Question:

Should the API be Python or TypeScript?

Recommendation:

Use Python for API and workers initially because analysis, embeddings,
clustering, and data processing will be Python-heavy.

### MCP Server Language

Question:

Should MCP server be Python or TypeScript?

Options:

- Python: easier access to backend packages
- TypeScript: strong MCP ecosystem and web tooling alignment

Recommendation:

Start in Python if API and context packages are Python. Keep protocol logic
thin so it can be rewritten later if needed.

### First Vector Store

Question:

Should MVP start with pgvector or Qdrant?

Recommendation:

Start with pgvector for simplest local setup, but implement VectorStore
interface and add Qdrant quickly. Public docs should recommend Qdrant for
larger datasets.

### First Demo

Options:

- website/GEO audit
- CSV company benchmark
- sales-call transcript analysis

Recommendation:

Build website/GEO first because there is prior project code and it creates a
strong visual demo. Add CSV cohort comparison immediately after because it
proves generality.

### Entity Mapper Complexity

Question:

How much UI should exist in MVP?

Recommendation:

Start with CLI/config-driven mapping for CSV/JSONL and a simple UI preview.
Do not build a full visual mapper before the analysis loop works.

### Local LLM

Question:

Should MVP include local LLM support?

Recommendation:

Include local embedding support first. Add local LLM after context packs and
MCP work. LLM is useful, but deterministic analysis should produce value first.

### First Live-Agent Subscription Demo

Question:

Which module should prove streaming agent context first?

Options:

- Product Event Intelligence: trial account upgrade scoring
- Marketing Intelligence: paid keyword/content gap watcher
- Customer Support Intelligence: high-risk ticket escalation

Recommendation:

Start with Product Event Intelligence if we want the clearest real-time agent
story. Start with Marketing if we want the strongest connection to the original
website/GEO direction. Both reuse the same context subscription core.

## Major Risks

### Scope Explosion

Risk:

The platform can become too broad.

Mitigation:

- build one universal model
- ship two strong demos
- keep connectors minimal
- make analysis engine reusable

### Weak Open-Source Value

Risk:

Community edition feels like a teaser.

Mitigation:

- include real import/analyze/MCP flow
- make local setup easy
- include sample data
- publish good examples

### Vector Dashboard Trap

Risk:

Product becomes only a map of points.

Mitigation:

- focus on business questions
- connect insights to metrics
- always provide recommendations and evidence
- make context packs central

### Agent Security

Risk:

MCP exposes too much data or unsafe tools.

Mitigation:

- read-only by default
- strict permissions
- redaction
- audit logs
- action tools separately enabled
- source content treated as untrusted evidence
- agent sessions are authenticated and audited
- read-only MCP mode is the default

### Model Drift And Reproducibility

Risk:

Embeddings and LLM summaries change over time.

Mitigation:

- store model versions
- store content hashes
- immutable analysis runs
- context pack snapshots
- reproducible artifact metadata

### Streaming Complexity

Risk:

Streaming, backfills, and reprocessing can make the MVP too complex.

Mitigation:

- start with periodic sync and source_events
- use at-least-once processing with idempotent writes
- add webhooks before Kafka-style streams
- keep full event streaming as an enterprise-scale phase
- make raw event retention configurable

## Near-Term Next Actions

1. Decide license.
2. Rename workspace/repo to `meaninggrid` when ready.
3. Create monorepo skeleton.
4. Add Docker Compose.
5. Add Postgres migrations for core model.
6. Add CLI import for JSONL/CSV.
7. Port useful website crawler ideas from `../site-audit`.
8. Add embedding provider and pgvector search.
9. Add analysis engine MVP.
10. Add MCP server with dataset card and context pack tools.
11. Add source event log and idempotent incremental ingestion.
12. Add reprocessing framework after the first analysis loop works.
13. Add headless profile and agent session model.
14. Add module registry and first Marketing/VC/Product Event module manifests.
