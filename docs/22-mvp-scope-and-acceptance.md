# MVP Scope And Acceptance

## Purpose

This document freezes the first buildable version of MeaningGrid.

The goal is not to implement the whole platform. The goal is to build the
smallest local application that proves the architecture:

```text
local Docker -> crawl website -> model entities -> embed content -> analyze
-> explain with evidence -> expose through UI/API/MCP
```

The wider MeaningGrid architecture stays visible in the data model and module
contracts, but v0 should be small enough for a developer team to build without
wandering.

## Product Slice

Version name:

```text
MeaningGrid v0.1: Local Site Audit
```

Primary use case:

```text
Run MeaningGrid locally, crawl one website, analyze technical SEO, semantic
structure, duplicate content, outlier pages, internal link opportunities, and
basic GEO readiness.
```

Primary user:

```text
developer, founder, SEO/GEO consultant, agency operator
```

Primary interface:

```text
web UI
```

Secondary interfaces:

```text
REST API
CLI
MCP server
```

## V0.1 Includes

### Local Runtime

- Docker Compose local stack
- web app
- API service
- worker service
- scheduler service
- MCP server process
- Postgres with pgvector
- Redis
- MinIO
- Qdrant
- idempotent migrations
- idempotent local seed
- bundled Site Audit module

### Core Model

- tenant
- local user
- workspace
- dataset
- module installation
- source
- raw object
- source event
- entity type
- relation definition
- metric definition
- entity
- entity relation
- content unit
- content chunk
- metric value
- embedding model
- embedding run
- embedding metadata
- analysis run
- analysis artifact
- insight
- evidence
- job
- audit event

### Site Audit Module

- site audit dataset template
- website crawler
- sitemap discovery
- robots/noindex/canonical extraction
- page entity creation
- paragraph and heading extraction
- internal/external link extraction
- raw HTML storage
- technical SEO metrics
- semantic embeddings
- page clusters
- page outliers
- duplicate/near-duplicate pages
- paragraph similarity
- internal link opportunities
- basic GEO readiness scoring
- page detail evidence
- report generation baseline
- MCP prompts for audit questions

### UI

- workspace shell
- dataset list
- new Site Audit wizard
- crawl job status
- site overview
- pages table
- page detail
- technical issues
- semantic clusters
- outliers
- duplicates
- internal link opportunities
- GEO readiness
- insights with evidence
- MCP setup page

### API

- health/version
- workspace read
- dataset create/list/detail
- site crawl start
- job status
- pages list/detail
- content/evidence read
- analysis start/status
- artifacts read
- insights/evidence read
- semantic search
- context pack create/read
- module list

### MCP

- list datasets
- get dataset card
- semantic search
- get page profile
- get insight evidence
- build context pack
- prompts:
  - `/audit_site_geo`
  - `/explain_page_outlier`
  - `/find_content_gaps`
  - `/find_internal_link_opportunities`
  - `/prepare_content_brief`

## V0.1 Excludes

Do not build these in v0.1:

- SaaS billing
- multi-tenant hosted admin console
- OIDC/SSO
- advanced RBAC/ABAC
- paid module marketplace
- streaming-agent subscriptions
- ClickHouse requirement
- Temporal requirement
- Kafka/Redpanda requirement
- full Marketing/VC/Sales/Support modules
- Google Search Console connector
- Google Ads connector
- ecommerce connector
- local LLM runtime requirement
- collaborative editing
- advanced report builder
- custom user-defined modules in UI
- domain monitoring scheduler beyond simple recrawl job shape

The schema can reserve clean extension points for these, but v0.1 should not
implement them.

## Happy Path

```text
1. Developer runs docker compose up --build.
2. Seed creates local tenant, workspace, user, and Site Audit module.
3. User opens http://localhost:3000.
4. User creates a Site Audit dataset.
5. User enters https://example.com and crawl limit.
6. Worker crawls pages and stores raw HTML.
7. Worker extracts page metadata, paragraphs, headings, and links.
8. Worker creates entities, content units, chunks, relations, and metrics.
9. Worker embeds chunks and page summaries.
10. Worker runs Site Audit v0 analysis.
11. UI shows overview, issues, clusters, outliers, duplicates, and GEO score.
12. User opens a page detail and sees evidence.
13. User generates a simple report.
14. MCP client can query the dataset.
```

## Developer Demo Command

The first complete demo should work with:

```bash
docker compose up --build
```

Then either:

```bash
meaninggrid import website https://example.com --max-pages 50
meaninggrid analyze latest --preset site_audit_v0
```

Or through the web UI.

## Acceptance Criteria

### Local Runtime

- `docker compose up --build` starts all required services.
- `GET /health` returns ok.
- Web UI loads at `http://localhost:3000`.
- API docs or OpenAPI JSON is available.
- Migrations run once and are idempotent.
- Seed can run repeatedly without duplicate module records.
- Worker can process jobs.
- MinIO buckets are created.
- Qdrant starts as a required local service.
- `GET /health` reports Qdrant as `vector_store=ok`.
- Qdrant collection can be created.

### Crawl

- User can start a crawl for one domain.
- Crawl respects max page limit.
- Crawl stores raw HTML as raw objects.
- Crawl creates source events.
- Crawl handles at least:
  - 200 page
  - 301/302 redirect
  - 404 page
  - duplicate URL discovered twice
- Crawl records errors without killing the full run.

### Entity And Content Model

- Domain, crawl run, page, paragraph, heading, and link entities are created.
- Page entity has URL, final URL, title, meta description, status code.
- Paragraphs become content units.
- Content chunks are created from content units.
- Links become entity relations or external link records.
- Metric values are attached to pages and crawl run.

### Embeddings

- Embedding run can be started.
- Unchanged chunks are skipped on re-run.
- Embeddings are written to Qdrant by default.
- pgvector remains available for fallback/minimal mode.
- Semantic search returns chunks with entity/page references.
- Vector payload includes tenant, workspace, dataset, entity, content unit, and
  classification fields.

### Analysis

- Technical issue artifacts are generated.
- Semantic clusters are generated.
- Outlier pages are generated.
- Duplicate/near-duplicate page pairs are generated.
- Basic GEO readiness scores are generated.
- Insights link to evidence.
- Analysis run status moves to succeeded or failed.

### UI

- User can see crawl progress.
- User can see pages table.
- User can filter pages by issue type.
- User can open page detail.
- User can see clusters/outliers/duplicates.
- User can see evidence for an insight.
- User can generate a basic report.

### MCP

- MCP server starts.
- MCP client can list datasets.
- MCP client can get dataset card.
- MCP client can search website content.
- MCP client can build a Site Audit context pack.
- MCP client can retrieve evidence for one insight.

## Quality Gates

Before v0.1 is considered done:

- unit tests for entity/content/metric creation
- unit tests for URL normalization
- unit tests for HTML extraction
- unit tests for scoring formulas
- integration test for 5-page fixture website
- integration test for crawl -> analyze pipeline
- API test for happy path
- Playwright smoke test for main UI flow
- MCP smoke test for dataset card and search
- Docker Compose fresh-start test

## Fixture Requirements

Create a local fixture website with:

- home page
- product/service page
- duplicate page
- semantically unrelated outlier page
- page with missing title
- page with missing meta description
- broken internal link
- internal link opportunity not currently linked
- paragraph duplicated across two pages

Fixture expected results:

- duplicate pair is detected
- outlier page is detected
- missing metadata issues are detected
- broken link issue is detected
- at least one internal link opportunity is suggested
- semantic clusters are produced

## V0.1 Success Definition

The release is successful if a new user can run MeaningGrid locally, crawl a
small website, and understand:

- what technical issues exist
- what semantic clusters exist
- which pages are outliers
- which pages are duplicated or cannibalizing
- which internal links should be added
- which pages are weak for GEO
- what evidence supports every important recommendation

If that works, the platform has proven its core loop.
