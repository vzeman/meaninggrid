# Implementation Backlog

The first implementation slice is specified in:

- [MVP Scope And Acceptance](22-mvp-scope-and-acceptance.md)
- [Initial Database Schema V0](23-initial-database-schema-v0.md)
- [Site Audit V0 Pipeline And Analysis](24-site-audit-v0-pipeline-and-analysis.md)
- [API Contract V0](25-api-contract-v0.md)
- [Worker Jobs And State Machines](26-worker-jobs-and-state-machines.md)
- [UI Information Architecture V0](27-ui-information-architecture-v0.md)
- [Development Skeleton And First Sprints](28-development-skeleton-and-first-sprints.md)

## Epic 1: Repository And Developer Experience

Tasks:

- create monorepo structure
- choose package manager
- add linting and formatting
- add Docker Compose
- add default local Docker profile
- add analytics and local-ai Docker profiles
- add Postgres + pgvector service
- add Redis service
- add MinIO service
- add Qdrant service
- add headless Docker Compose profile
- add environment configuration
- add idempotent migration/seed command
- add health checks
- add contribution docs

Acceptance criteria:

- developer can clone and start services locally
- `docker compose up --build` starts web, API, worker, MCP, and storage
- docs explain required dependencies
- API health endpoint works
- tests can run locally

## Epic 2: Core Database Model

Tasks:

- add Postgres service
- set up migrations
- implement tenants
- implement agent_sessions
- implement label_definitions
- implement modules
- implement module_versions if needed for bundled modules
- implement module_installations
- implement module_resources
- implement workspaces
- implement datasets
- implement sources
- implement raw_objects
- implement data_streams
- implement source_events
- implement entity_types
- implement entities
- implement entity_versions
- implement entity_change_events
- implement relations
- implement content_units
- implement content_chunks
- implement metric_definitions
- implement metric_values
- implement labels_json and classification_json on core records
- implement analysis_runs
- implement artifacts
- implement insights and evidence
- seed bundled Site Audit module resources

Acceptance criteria:

- migrations create all core tables
- seed script creates local tenant/workspace
- seed script installs Site Audit module idempotently
- API can create and read dataset
- tests cover entity/content/metric creation

## Epic 3: CLI

Tasks:

- add `meaninggrid` CLI
- add config loading
- add local API connection
- add import commands
- add embedding command
- add analyze command
- add search command
- add MCP start command

Acceptance criteria:

```bash
meaninggrid --help
meaninggrid import jsonl ./examples/support-tickets/tickets.jsonl
meaninggrid analyze ds_123
```

## Epic 4: CSV And JSONL Import

Tasks:

- upload or read local file
- parse CSV
- parse JSONL
- infer columns/types
- create entity mapping config
- create entities
- create content units
- create metric values
- store raw object metadata
- support labels and classification in imported rows/events

Acceptance criteria:

- example company benchmark CSV imports successfully
- text fields become content units
- numeric fields become metrics
- import job records status and errors

## Epic 5: Website Import

Tasks:

- basic crawler
- sitemap discovery
- URL filters
- page fetch
- HTML snapshot storage
- main text extraction
- paragraph extraction
- heading extraction
- link extraction
- canonical/noindex handling
- entity/content/relation creation

Acceptance criteria:

- small website imports 50-100 pages
- pages become entities
- paragraphs and headings become content units
- links become relations

## Epic 6: Embeddings

Tasks:

- embedding provider interface
- local sentence-transformers provider
- OpenAI provider optional
- embedding model registry
- chunk batching
- content hash checks
- pgvector adapter
- Qdrant adapter
- embedding run status

Acceptance criteria:

- chunks can be embedded
- re-run skips unchanged chunks
- semantic search returns relevant chunks
- vector metadata records model and content hash

## Epic 7: Analysis Engine

Tasks:

- centroid metrics
- pairwise stats
- focus/radius
- clustering
- c-TF-IDF labels
- outlier detection
- duplicate detection
- UMAP projection
- artifact writing

Acceptance criteria:

- `meaninggrid analyze` creates artifacts
- UI/API can list clusters and outliers
- fixture tests detect known duplicate/outlier examples

## Epic 8: Cohort Analysis

Tasks:

- define cohort spec
- filter entities by metric/property
- compute cohort centroids
- compare cluster enrichment
- find nearest successful analogs
- generate success pattern candidates
- attach evidence

Acceptance criteria:

- company benchmark demo compares top vs weak companies
- calls demo compares won vs lost calls
- output includes evidence chunks

## Epic 9: Context Layer

Tasks:

- dataset card builder
- entity type card builder
- analysis summary builder
- evidence pack builder
- context budgeter
- context pack table
- context pack API

Acceptance criteria:

- context pack can be built for a dataset and task
- context pack includes schema, metrics, findings, evidence links
- budget setting affects included detail

## Epic 10: MCP Server

Tasks:

- MCP server process
- auth/token handling
- agent session handling
- list resources
- read resources
- implement discovery tools
- implement search tools
- implement build_context_pack
- implement get_evidence
- implement prompts
- audit MCP calls

Acceptance criteria:

- MCP client can list datasets
- MCP client can build a context pack
- MCP client can search context
- MCP client can retrieve evidence
- MCP server can run without the web app

## Epic 11: Web UI MVP

Tasks:

- layout and navigation
- workspace selector
- dataset catalog
- import page
- job status
- entity browser
- semantic map
- clusters table
- outliers table
- duplicates table
- insight detail
- evidence drawer
- MCP setup page

Acceptance criteria:

- user can import dataset, run analysis, and inspect result
- semantic map handles at least 5k points through sampling or canvas
- evidence is accessible from insights

## Epic 12: Security Baseline

Tasks:

- local auth
- API tokens
- RBAC tables
- permission middleware
- tenant scoping
- raw-source access checks
- audit log table
- PII redaction utility baseline
- MCP read-only mode

Acceptance criteria:

- API rejects cross-tenant access
- MCP results are permission-scoped
- raw-source access is logged
- context pack can be generated with redaction

## Epic 13: Reports And Exports

Tasks:

- HTML report generator
- JSON artifact export
- CSV table export
- report templates
- report API
- downloadable report bundle

Acceptance criteria:

- website demo produces a report
- company benchmark demo produces a report
- all insight claims include evidence references

## Epic 14: Deployment

Tasks:

- Docker Compose production profile
- Docker Compose headless profile
- Helm chart
- environment docs
- backup docs
- Qdrant config
- MinIO/S3 config
- worker scaling docs

Acceptance criteria:

- local compose works
- headless compose works without the web app
- single-node deployment works
- Helm chart can install core services in a test cluster

## Epic 15: Streaming And Incremental Data

Tasks:

- implement data_streams table
- implement source_events table
- implement entity_change_events table
- add idempotency keys
- add periodic sync scheduler
- add webhook ingestion endpoint
- add recent changes API
- add stream status API
- add backfill job type
- add dead-letter handling

Acceptance criteria:

- duplicate events are ignored
- new events update current entity state
- changed content invalidates embeddings
- changed metrics invalidate affected analysis artifacts
- stream status shows watermark and errors

## Epic 15b: Module Framework

Tasks:

- define module manifest schema
- implement modules table
- implement module_installations table
- implement module_resources table
- implement module registry loader
- validate module manifests
- register entity schemas from modules
- register metric definitions from modules
- register analysis presets from modules
- register context templates from modules
- register MCP prompts from modules
- register label and filter presets from modules
- add module install/list API
- add CLI module install/list commands

Acceptance criteria:

- module can be installed into a workspace
- module schemas are available during dataset creation
- module analysis presets can be executed
- module MCP prompts appear in the MCP server
- installed module version is recorded in analysis/context artifacts

## Epic 15c: Push, Labeling, And Filtering

Tasks:

- define canonical push envelope
- implement JSONL push endpoint
- implement JSON batch push endpoint
- implement document push endpoint
- implement metric push endpoint
- implement relation push endpoint
- implement idempotency keys
- implement label_definitions
- add labels_json to core records
- add classification_json to core records
- implement label propagation
- define filter grammar
- implement SQL filter compiler
- implement vector-store filter compiler
- add MCP filter support
- add label registry API

Acceptance criteria:

- pushed events can create entities, content units, metrics, and relations
- duplicate events are idempotent
- labels propagate from dataset/source to chunks/vectors
- semantic search can filter by labels, classification, and time
- analysis runs can be scoped by filters
- MCP tools apply user filters and automatic access filters

## Epic 16: Reprocessing Framework

Tasks:

- implement derivation_specs
- implement derived_artifacts
- track chunking/embedding/metric extractor versions
- add artifact invalidation
- add reprocessing job
- add reprocess-from-raw workflow
- add superseded artifact status

Acceptance criteria:

- user can add a new metric extractor and run it on historical raw data
- old analysis runs remain available
- new derived artifacts point to the new spec version
- context packs show which derivation version they used

## Epic 17: Marketing Streams Demo

Tasks:

- define marketing project template
- add Google Search Console connector stub or importer
- add Google Ads CSV/API importer
- add ecommerce orders JSONL/webhook importer
- model keywords, queries, campaigns, pages, products, orders
- implement keyword-to-page semantic alignment
- implement campaign-to-content gap analysis
- add demo report

Acceptance criteria:

- user can import or sync marketing metrics
- system finds paid keywords far from existing website content
- report links cost/conversion metrics to semantic content gaps
- MCP can build a delta context pack for new keyword mismatches

## Epic 18: VC Module Demo

Tasks:

- define VC module manifest
- add startup/founder/deck/memo/entity schemas
- add invested/refused cohort mappings
- add pitch deck JSONL/PDF import fixture
- add startup similarity analysis preset
- add investment context-pack template
- add VC MCP prompts
- add demo report

Acceptance criteria:

- new startup can be compared to invested and rejected cohorts
- agent can prepare an investment context pack
- output includes nearest analogs, risk themes, and evidence

## Epic 19: Product Event Module Demo

Tasks:

- define Product Event module manifest
- add account/user/session/event schemas
- add event JSONL push fixture
- add trial conversion metric fixture
- add converted/non-converted cohort mapping
- implement event sequence summary derivation
- implement trial upgrade scoring analysis preset
- add account journey context-pack template
- add Product Event MCP prompts
- add demo report

Acceptance criteria:

- user can push application/website events into a dataset
- system can score active trial accounts
- account score includes evidence and nearest converter/non-converter analogs
- agent can recommend next best actions for trial accounts

## Epic 20: Streaming Agent Context Engine

Tasks:

- extend source_events with partition_key, sequence, priority_hint, route_hint
- implement event_routes table
- add deterministic routing rules
- add routing rule audit output
- implement context_units table
- build product trial account journey context unit
- build marketing keyword/content gap context unit
- build support ticket timeline context unit
- embed context units for semantic retrieval
- implement agent_subscriptions table
- implement context_notifications table
- expose context-stream and context-unit MCP resources
- implement subscribe_context MCP tool
- implement list_changed_context MCP tool
- implement ack_context_notification MCP tool
- implement read_context_unit MCP tool
- implement routing_feedback MCP tool
- add replay from last acknowledged sequence
- add notification deduplication tests
- implement shared_memory_items table
- add save_shared_memory and forget_shared_memory tools

Acceptance criteria:

- agent can subscribe to context changes with filters and priority threshold
- fast-path event creates a notification within the target latency budget
- agent can pull the related context unit through MCP
- agent can acknowledge the notification and submit routing feedback
- reconnect can resume from the last acknowledged sequence
- source event lineage and evidence are preserved

## First Sprint Plan

Goal:

Create the foundation and import one JSONL dataset.

Tasks:

1. Create monorepo skeleton.
2. Add API service with health endpoint.
3. Add Postgres and migrations.
4. Implement workspaces/datasets/entities/content units.
5. Add JSONL importer.
6. Add CLI command for JSONL import.
7. Add minimal tests.

End-of-sprint demo:

```bash
docker compose up
meaninggrid import jsonl examples/support-tickets/tickets.jsonl
curl http://localhost:8000/datasets
```

## Second Sprint Plan

Goal:

Embed and search imported content.

Tasks:

1. Add embedding model registry.
2. Add local embedding provider.
3. Add pgvector.
4. Add embedding worker job.
5. Add semantic search endpoint.
6. Add CLI search command.

End-of-sprint demo:

```bash
meaninggrid embed ds_123
meaninggrid search ds_123 "login problems after update"
```

## Third Sprint Plan

Goal:

Run first semantic analysis.

Tasks:

1. Add centroid metrics.
2. Add clustering.
3. Add outlier detection.
4. Add duplicate detection.
5. Add analysis artifacts.
6. Add basic HTML/JSON output.

End-of-sprint demo:

```bash
meaninggrid analyze ds_123
meaninggrid artifacts ds_123
```

## Fourth Sprint Plan

Goal:

Expose context to agents.

Tasks:

1. Add dataset card.
2. Add context pack builder.
3. Add MCP server.
4. Add MCP resources.
5. Add search_context tool.
6. Add get_evidence tool.

End-of-sprint demo:

An MCP client can ask:

```text
What datasets are available?
Build a context pack for support-ticket analysis.
Find similar tickets about login problems.
```

## Release 0.1 Criteria

MeaningGrid 0.1 should include:

- local Docker Compose
- CSV/JSONL import
- basic website import
- embeddings
- semantic search
- clustering
- outliers
- duplicates
- context packs
- MCP server
- basic UI
- examples
- docs

## Release 0.2 Criteria

MeaningGrid 0.2 should include:

- cohort comparison
- website/GEO demo polish
- company benchmark demo
- Qdrant support documented
- improved UI
- report generation
- basic RBAC
- audit logs

## Release 0.3 Criteria

MeaningGrid 0.3 should include:

- support-ticket connector/demo
- call transcript demo
- PII redaction
- Helm chart
- SSO/OIDC baseline
- enterprise deployment docs

## Release 0.4 Criteria

MeaningGrid 0.4 should include:

- periodic stream support
- webhook ingestion
- source event log
- reprocessing framework
- backfill framework
- marketing stream demo
- recent-changes MCP tools
- basic monitors and alerts

## Release 0.5 Criteria

MeaningGrid 0.5 should include:

- module registry
- module manifest validation
- Marketing module
- VC module
- Product Event module
- module MCP prompt registration
- module analysis preset registration
- module context-pack template registration

## Release 0.6 Criteria

MeaningGrid 0.6 should include:

- streaming event routing
- context units
- MCP context subscriptions
- context notification ack/resume
- routing feedback
- shared memory items
- one live-agent demo for Product Events, Marketing, or Support
