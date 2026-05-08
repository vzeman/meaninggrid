# Local Docker Infrastructure And Flexible Schema

## Purpose

The first MeaningGrid release should feel like a local appliance:

```bash
cp .env.example .env
docker compose up --build
```

After that, the user should have:

- web UI
- API
- worker
- scheduler
- MCP server
- Postgres with pgvector
- Redis queue/cache
- Qdrant vector store
- MinIO object storage
- optional ClickHouse analytics store
- optional local embedding/LLM runtime
- default Site Audit and GEO module installed

The user should be able to crawl a website, analyze it deeply, view results in
the UI, and expose the same dataset to AI agents through MCP without signing up
for any cloud service.

## First Version Promise

The local distribution should support this path:

```bash
docker compose up --build
open http://localhost:3000
```

Then in the UI:

```text
Create workspace -> Create Site Audit dataset -> Crawl domain -> Analyze
```

And from CLI/API:

```bash
meaninggrid import website https://example.com --dataset "Example Site"
meaninggrid analyze ds_123 --preset site_audit_full
meaninggrid mcp start
```

The first local version should not require:

- Kubernetes
- cloud object storage
- managed vector DB
- managed Postgres
- SaaS auth
- external LLM provider

External providers can be optional accelerators, not requirements.

## Docker Compose Profiles

### Default Profile

The default profile should run the complete local product while staying
reasonable for a developer laptop.

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

Recommended command:

```bash
docker compose up --build
```

### Analytics Profile

Adds ClickHouse for higher-volume event and metric analytics.

Services added:

```text
clickhouse
```

Recommended command:

```bash
docker compose --profile analytics up --build
```

Use this when:

- marketing streams become large
- source event exploration needs fast aggregations
- product event scoring needs large event history
- local machine has enough RAM

### Local AI Profile

Adds local model runtime for offline embedding or local LLM features.

Services added:

```text
ollama or vllm
embedding-server
```

Recommended command:

```bash
docker compose --profile local-ai up --build
```

The core system should still work without this profile by using a small
sentence-transformers model inside the worker image or an external embedding
provider configured in `.env`.

### Headless Profile

Runs without the web app.

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
```

Recommended command:

```bash
docker compose --profile headless up --build
```

This is the default shape for AI-agent infrastructure and secure deployments.

### Minimal Profile

Runs with only Postgres/pgvector and no Qdrant or MinIO.

Services:

```text
postgres
redis
api
worker
mcp-server
web
```

Use this for tests, tiny demos, and low-resource machines.

## Local Service Map

| Service | Role | Default Port | Required |
|---|---|---:|---|
| `web` | Next.js UI | 3000 | yes |
| `api` | FastAPI backend | 8000 | yes |
| `mcp-server` | MCP resources/tools/prompts | 8010 | yes |
| `worker` | Background jobs | none | yes |
| `scheduler` | Periodic jobs | none | yes |
| `postgres` | Source of truth + pgvector | 5432 | yes |
| `redis` | Queue, cache, event bus MVP | 6379 | yes |
| `minio` | Raw payloads and artifacts | 9000/9001 | yes |
| `qdrant` | Scalable vector search | 6333/6334 | yes |
| `clickhouse` | High-volume analytics | 8123 | optional |
| `ollama`/`vllm` | Local LLM | 11434/8001 | optional |
| `embedding-server` | Local embedding service | 8100 | optional |

Only `web`, `api`, and `mcp-server` need to be user-facing. Storage ports can
remain internal by default and be exposed only for development.

## Docker Images

Use two application images at first:

```text
meaninggrid-backend
meaninggrid-web
```

`meaninggrid-backend` can run multiple commands:

```text
api
worker
scheduler
mcp-server
cli
migrate
seed
```

This avoids maintaining separate Dockerfiles while the project is young.
Later, enterprise builds can split images.

## Suggested Compose Layout

```text
deployments/
  docker-compose/
    docker-compose.yml
    docker-compose.analytics.yml
    docker-compose.local-ai.yml
    docker-compose.headless.yml
    .env.example
    init/
      postgres/
      minio/
```

Root developer shortcuts:

```text
docker-compose.yml -> deployments/docker-compose/docker-compose.yml
.env.example -> deployments/docker-compose/.env.example
```

## Persistent Volumes

Use named Docker volumes:

```text
meaninggrid_postgres_data
meaninggrid_qdrant_data
meaninggrid_minio_data
meaninggrid_redis_data
meaninggrid_clickhouse_data
meaninggrid_model_cache
```

Object storage buckets:

```text
meaninggrid-raw
meaninggrid-artifacts
meaninggrid-exports
meaninggrid-backups
```

Folder conventions inside object storage:

```text
raw/{tenant_id}/{workspace_id}/{dataset_id}/{source_id}/...
artifacts/{tenant_id}/{workspace_id}/{dataset_id}/{analysis_run_id}/...
exports/{tenant_id}/{workspace_id}/{dataset_id}/...
backups/{timestamp}/...
```

## Boot Sequence

The local stack should start predictably.

1. Postgres starts and accepts connections.
2. Redis, MinIO, and Qdrant start.
3. API waits for dependencies.
4. Migration command runs Alembic migrations.
5. Seed command creates local tenant, admin user, workspace, and default module
   registry.
6. Site Audit module is installed into the local workspace.
7. Worker and scheduler start.
8. MCP server starts.
9. Web app starts and points to API.

The seed command must be idempotent. Running `docker compose up` twice should
not duplicate modules, label definitions, metric definitions, or demo data.

## Environment Configuration

`.env.example` should include:

```text
MEANINGGRID_ENV=local
MEANINGGRID_PUBLIC_URL=http://localhost:3000
API_PUBLIC_URL=http://localhost:8000
MCP_PUBLIC_URL=http://localhost:8010

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=meaninggrid
POSTGRES_USER=meaninggrid
POSTGRES_PASSWORD=meaninggrid

REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=meaninggrid
S3_SECRET_KEY=meaninggrid-local
S3_BUCKET_RAW=meaninggrid-raw
S3_BUCKET_ARTIFACTS=meaninggrid-artifacts

VECTOR_BACKEND=qdrant
OBJECT_STORE_BACKEND=s3
QUEUE_BACKEND=redis
EMBEDDING_PROVIDER=local
LLM_PROVIDER=none

DEFAULT_MODULES=site_audit
ENABLE_TELEMETRY=false
```

Secrets in local mode can be simple, but the same settings should map to real
secret managers in enterprise deployments.

## Runtime Package Structure

Recommended monorepo shape:

```text
meaninggrid/
  apps/
    api/
    web/
    worker/
    mcp-server/
  packages/
    core/
    db/
    connectors/
    ingestion/
    analysis/
    context/
    streaming-context/
    embeddings/
    vectorstores/
    objectstore/
    reports/
    security/
    modules/
  modules/
    site-audit/
    marketing/
    vc/
    product-events/
  migrations/
    core/
    modules/
  deployments/
    docker-compose/
    helm/
  examples/
    site-audit/
    company-benchmark/
    support-tickets/
```

The `modules/site-audit` package should be bundled and enabled by default. Paid
or enterprise modules can be distributed later as signed module packages.

Programming language guidance for each package is defined in:
[Language And Runtime Strategy](21-language-and-runtime-strategy.md).

## Database Design Principle

MeaningGrid should use a stable core schema and a flexible module layer.

Core tables should model things every module needs:

```text
tenant
workspace
dataset
source
stream
raw object
source event
entity
relation
content
metric
embedding
analysis
insight
evidence
context
module
audit
policy
job
```

Module-specific detail should start as:

```text
properties_json
labels_json
classification_json
dimensions_json
artifact_json
config_json
```

Promote module-specific fields into first-class columns or extension tables
only when:

- the field is used in many filters
- the field needs a special index
- the field needs referential integrity
- the field becomes part of a public contract
- query performance requires it

This keeps the open-source core flexible without turning every module into a
schema fork.

## Table Families

### 1. Identity, Tenancy, And Access

Tables:

```text
tenants
users
service_accounts
api_tokens
workspaces
workspace_members
roles
permissions
access_policies
agent_sessions
audit_events
```

Purpose:

- local admin user
- multi-workspace support
- future SaaS multi-tenancy
- API/MCP authorization
- auditability

MVP can simplify users and auth, but tenant/workspace IDs should exist from the
first migration. Retrofitting tenancy later is painful.

### 2. Modules And Configuration

Tables:

```text
modules
module_versions
module_installations
module_resources
module_migrations
module_entitlements
runtime_settings
feature_flags
```

Purpose:

- install Site Audit by default
- install optional modules later
- know which module registered which schema, metric, analysis, prompt, or
  dashboard
- support paid module licensing later

`module_resources.resource_type` examples:

```text
entity_type
relation_type
metric_definition
connector
mapping_preset
analysis_preset
dashboard
report_template
context_template
context_unit_builder
context_subscription_template
mcp_prompt
monitor_template
```

### 3. Dataset And Source Lifecycle

Tables:

```text
datasets
dataset_versions
sources
data_streams
connector_runs
sync_runs
jobs
job_events
```

Purpose:

- track datasets such as one website audit or one competitor comparison
- track connectors and crawl runs
- show import/sync/analyze progress in UI
- resume failed work

Dataset kinds for first version:

```text
site_audit
domain_comparison
custom
```

### 4. Raw Data And Event Log

Tables:

```text
raw_objects
source_events
event_routes
rejected_events
dead_letter_events
entity_change_events
```

Purpose:

- preserve original HTML, robots, sitemap, API payloads, files, and webhooks
- support replay and reprocessing
- deduplicate events
- route events to fast/batch/archive paths

Rules:

- `source_events` are append-only.
- `raw_objects` are immutable references to object storage.
- `entity_change_events` are append-only normalized changes.
- current entity state is a projection, not the only truth.

### 5. Schema Registry

Tables:

```text
entity_types
property_definitions
relation_definitions
metric_definitions
label_definitions
dimension_definitions
classification_policies
mapping_presets
validation_rules
```

Purpose:

- let modules define structured schemas without hardcoding them in the app
- allow UI forms and import mappers to be generated
- keep label and metric naming consistent
- prevent module drift

Example:

The Site Audit module registers `page`, `paragraph`, `heading`, `link`,
`crawl_run`, and `domain` entity types. Marketing registers `keyword`,
`campaign`, `ad_group`, and `search_query`.

### 6. Normalized Entity Graph

Tables:

```text
entities
entity_versions
entity_relations
entity_relation_versions
entity_aliases
entity_merge_records
```

Purpose:

- represent pages, paragraphs, companies, calls, tickets, products, and custom
  business objects
- preserve historical changes
- support graph traversal and evidence

Core entity columns:

```text
id
tenant_id
workspace_id
dataset_id
entity_type_id
external_id
label
description
canonical_uri
raw_object_id
properties_json
labels_json
classification_json
source_created_at
source_updated_at
created_at
updated_at
```

### 7. Content And Chunks

Tables:

```text
content_units
content_chunks
content_extractions
```

Purpose:

- store extracted page text, paragraphs, headings, transcript turns, emails,
  document sections, and spreadsheet rows
- provide stable units for embeddings and evidence
- allow re-chunking when strategies change

Site Audit examples:

```text
page_body
main_content
paragraph
heading
title
meta_description
schema_jsonld
anchor_text
image_alt_text
```

### 8. Metrics And Observations

Tables:

```text
metric_definitions
metric_values
metric_rollups
observation_windows
```

Purpose:

- store numeric, boolean, text, and JSON measurements
- support time windows and dimensions
- let modules add business-specific measurements

Metric values should support:

```text
entity_id
content_unit_id
observed_at
valid_from
valid_to
aggregation_window
dimensions_json
confidence
source_event_id
```

Site Audit metric examples:

```text
http_status_code
indexable
canonical_matches
title_length
meta_description_length
h1_count
word_count
internal_link_count
external_link_count
broken_outlink_count
duplicate_similarity
topical_focus_score
semantic_depth_score
geo_readiness_score
entity_coverage_score
answerability_score
centroid_distance
```

### 9. Embeddings And Vector Indexes

Tables:

```text
embedding_models
embedding_runs
embeddings
vector_collections
rerank_runs
```

Purpose:

- track embedding model identity
- prevent comparing incompatible vectors
- map database records to Qdrant/pgvector points
- support re-embedding

Rules:

- each embedding record points to entity/content/context target
- `content_hash` controls skip/recompute
- vector payload includes tenant/workspace/dataset/module/classification
- Qdrant is preferred for default local/full mode
- pgvector is fallback/minimal mode

### 10. Analysis And Artifacts

Tables:

```text
analysis_runs
analysis_artifacts
artifact_files
derivation_specs
derived_artifacts
cluster_memberships
projection_points
similarity_edges
insights
insight_evidence
```

Purpose:

- make analyses reproducible
- store outputs without forcing every analysis into a fixed table
- keep evidence connected to raw data
- allow invalidation and reprocessing

Artifact examples:

```text
site_audit_issue_table
semantic_cluster_table
page_similarity_matrix_sample
projection_2d
projection_3d
internal_link_graph
content_gap_table
domain_comparison_table
geo_readiness_report
```

### 11. Agent Context And Memory

Tables:

```text
context_packs
context_units
context_resource_versions
agent_subscriptions
context_notifications
shared_memory_items
routing_feedback
agent_notes
```

Purpose:

- let agents read compact, governed context
- support live subscriptions
- track notification delivery and feedback
- store explicit shared memory

### 12. Reports, Dashboards, And Exports

Tables:

```text
dashboard_definitions
dashboard_views
report_templates
reports
exports
saved_views
saved_filters
```

Purpose:

- allow modules to ship UI/report definitions
- keep reports reproducible
- let users save filtered views

For Site Audit, the default report templates should include:

```text
technical_seo_report
semantic_site_audit_report
geo_readiness_report
domain_comparison_report
content_brief_report
```

## Flexible Schema Rules

### Rule 1: Every Core Row Is Tenant/Workspace/Dataset Scoped

Most rows should include:

```text
tenant_id
workspace_id
dataset_id
```

Exceptions:

- global module definitions
- global embedding model registry
- local runtime settings

### Rule 2: Stable Columns For Identity, Flexible JSON For Domain Detail

Use columns for:

- IDs
- foreign keys
- type keys
- status
- timestamps
- source/update times
- labels/classification
- common names and descriptions

Use JSONB for:

- module-specific attributes
- source payload fragments
- analysis-specific output
- UI configuration
- connector settings

### Rule 3: Labels Are For Filtering, Properties Are For Description

Use labels for:

```text
module=site_audit
country=SK
language=en
status=needs_review
issue_type=duplicate_content
```

Use properties for:

```text
title="Pricing - ACME"
canonical_url="https://example.com/pricing"
meta_description="..."
```

Use metrics for:

```text
word_count=1280
internal_link_count=47
geo_readiness_score=0.72
```

### Rule 4: Module Tables Must Reference Core IDs

If a module later needs extension tables, they should never become a parallel
data universe.

Good:

```text
site_audit_page_scores.entity_id -> entities.id
site_audit_page_scores.analysis_run_id -> analysis_runs.id
```

Bad:

```text
site_audit_pages with no entity_id
```

### Rule 5: Derived Data Is Regenerable

Derived outputs should store:

- derivation_spec_id
- input_hash
- output_hash
- code_version
- model_version
- created_at
- invalidated_at

Raw objects and source events are durable. Chunks, embeddings, clusters,
summaries, and reports can be regenerated.

### Rule 6: Keep Module Migrations Optional

MVP modules should be mostly configuration:

- entity types
- metrics
- relation types
- mapping presets
- analysis presets
- dashboard definitions
- prompts

Module migrations are allowed later for performance or enterprise features, but
the default path should not require custom tables for every module.

## Default Bundled Module: Site Audit And GEO

The first open-source distribution should include the Site Audit module by
default. It becomes the proof that MeaningGrid is useful before customers buy
specialized modules.

Module key:

```text
site_audit
```

Dataset kinds:

```text
site_audit
domain_comparison
```

Default workflow:

```text
create dataset -> crawl domain -> extract content -> chunk -> embed -> analyze
-> inspect issues -> compare clusters -> generate report -> expose to MCP
```

## Site Audit Entity Types

Initial entity types:

```text
domain
crawl_run
page
page_snapshot
paragraph
heading
link
image
schema_markup
topic_cluster
competitor_domain
search_query
keyword
ai_prompt
ai_answer_observation
```

Minimal MVP can start with:

```text
domain
crawl_run
page
paragraph
heading
link
topic_cluster
```

## Site Audit Relations

Relation types:

```text
domain owns page
page has_snapshot page_snapshot
page contains paragraph
page contains heading
page links_to page
page links_to external_url
page canonical_of page
page redirects_to page
page similar_to page
page belongs_to topic_cluster
paragraph belongs_to page
heading belongs_to page
page targets keyword
page ranks_for search_query
domain competes_with domain
page competes_with page
ai_answer_observation cites page
```

## Site Audit Content Units

Content unit kinds:

```text
page_title
meta_description
h1
h2
h3
main_content
paragraph
anchor_text
image_alt
schema_jsonld
faq_item
author_bio
organization_facts
```

Each unit can be embedded separately. Paragraph-level embeddings allow:

- paragraph similarity
- duplicate paragraph detection
- weak-section detection
- semantic drift inside a page
- evidence snippets for recommendations

## Site Audit Metric Groups

### Crawl And Technical Metrics

```text
http_status_code
is_indexable
robots_allowed
has_noindex
canonical_present
canonical_matches_final_url
redirect_hop_count
content_type
html_size_bytes
load_time_ms
```

### On-Page Metrics

```text
title_length
title_missing
meta_description_length
meta_description_missing
h1_count
h2_count
word_count
paragraph_count
image_count
images_without_alt_count
schema_type_count
faq_count
```

### Link Graph Metrics

```text
internal_inlinks
internal_outlinks
external_outlinks
broken_outlinks
orphan_score
anchor_relevance_score
topic_link_coverage_score
```

### Semantic Metrics

```text
embedding_centroid_distance
topic_cluster_id
topical_focus_score
semantic_depth_score
duplicate_similarity_score
canonical_topic_overlap_score
cannibalization_risk_score
content_gap_score
paragraph_consistency_score
```

### GEO Metrics

GEO means generative engine optimization: how well a website can be understood,
trusted, cited, and used by AI answer engines and agents.

```text
answerability_score
entity_coverage_score
source_evidence_score
expertise_signal_score
freshness_signal_score
structured_data_coverage_score
comparison_readiness_score
definition_clarity_score
claim_evidence_density
brand_fact_consistency_score
```

## Site Audit Analysis Presets

### site_audit_technical

Finds:

- broken pages
- redirect chains
- non-indexable pages
- missing titles/descriptions
- duplicate titles/descriptions
- canonical problems
- robots/noindex issues
- broken internal and external links

### site_audit_semantic

Finds:

- semantic clusters
- outlier pages
- near-duplicate pages
- paragraph-level duplication
- pages far from domain/topic centroids
- weak or thin topic coverage
- content cannibalization
- internal linking gaps between semantically related pages

### site_audit_geo

Finds:

- weak entity clarity
- missing factual evidence
- missing definitions and comparisons
- weak answerability
- pages unlikely to be useful to AI agents
- inconsistent brand/product facts
- weak author/expertise signals
- schema/content mismatch

### domain_comparison

Compares multiple domains by:

- topic clusters
- content depth
- semantic coverage
- page similarity
- internal linking patterns
- GEO readiness
- technical quality
- unique and missing topic areas

### content_brief_generation

Builds evidence-backed briefs for:

- new pages
- page rewrites
- FAQ sections
- comparison pages
- internal link additions
- schema improvements

## Site Audit UI

Default pages:

```text
Workspace dashboard
Dataset list
New Site Audit wizard
Crawl status
Site overview
Technical issues
Semantic map
Clusters
Outliers
Duplicate content
Page detail
Paragraph evidence
Internal link graph
Domain comparison
GEO readiness
Reports
MCP setup
```

The first screen after creating a dataset should show the actual audit
experience, not a marketing landing page.

## Site Audit MCP Prompts

Prompts:

```text
/audit_site_geo
/explain_page_outlier
/compare_domains
/find_content_gaps
/find_internal_link_opportunities
/prepare_content_brief
/summarize_crawl_changes
/explain_geo_readiness
```

Example agent questions:

```text
Which pages are semantically far from the website centroid?
Which pages should be merged or canonicalized?
Which paragraphs are duplicated across pages?
Which internal links should we add?
Where is the website weak for AI answer engines?
Compare example.com and competitor.com by topic coverage.
Create a content brief for the biggest GEO gap.
```

## Paid Module Strategy

The open-source distribution can include Site Audit because it is the anchor
demo and useful on its own.

Paid or enterprise modules can later include:

- Marketing Intelligence with paid ad and ecommerce connectors
- VC Fund Intelligence
- Product Event Intelligence
- Legal Contract Intelligence
- Compliance/Audit Intelligence
- advanced enterprise connectors
- managed streaming infrastructure
- private deployment support

The business model should not make the open-source project feel empty. The
core plus Site Audit should be genuinely valuable locally.

## Initial Local MVP Tables

The first migration does not need every future table. A practical MVP can start
with:

```text
tenants
users
workspaces
workspace_members
modules
module_installations
module_resources
label_definitions
datasets
sources
data_streams
raw_objects
source_events
entity_types
relation_definitions
metric_definitions
entities
entity_versions
entity_relations
content_units
content_chunks
metric_values
embedding_models
embedding_runs
embeddings
analysis_runs
analysis_artifacts
insights
insight_evidence
context_packs
jobs
audit_events
```

Add these before streaming-agent features:

```text
event_routes
context_units
context_resource_versions
agent_sessions
agent_subscriptions
context_notifications
shared_memory_items
routing_feedback
```

Add these when modules and enterprise features mature:

```text
module_versions
module_migrations
module_entitlements
property_definitions
dimension_definitions
classification_policies
access_policies
saved_views
dashboard_definitions
report_templates
exports
dead_letter_events
derived_artifacts
derivation_specs
```

## Indexing Strategy

Postgres indexes:

```text
tenant_id, workspace_id, dataset_id on almost every table
dataset_id + entity_type_id on entities
dataset_id + external_id on entities
dataset_id + source_id + external_event_id on source_events
dataset_id + entity_id + observed_at on metric_values
dataset_id + content_hash on content_units/content_chunks
analysis_run_id on artifacts/insights
labels_json GIN where heavily filtered
properties_json GIN for exploratory filters
classification_json GIN for access filtering
```

Vector indexes:

```text
content_chunks
content_units
entities when entity summaries exist
context_units
insights when useful
```

Qdrant payload fields must include:

```text
tenant_id
workspace_id
dataset_id
module
entity_type
entity_id
content_unit_id
content_chunk_id
classification
access_policy_id
source_updated_at
labels
```

## Local Backup And Reset

Commands to provide:

```bash
meaninggrid backup create
meaninggrid backup restore ./backup.tar.zst
meaninggrid local reset
meaninggrid local reset --keep-raw
```

Backup should include:

- Postgres dump
- Qdrant snapshot
- MinIO bucket export
- ClickHouse dump if enabled
- `.env` template without secrets

Reset should clearly warn before deleting Docker volumes.

## Resource Targets

Default laptop target:

```text
RAM: 8-16 GB
CPU: 4 cores
Disk: 20+ GB free for crawls and vectors
```

Small profile:

```text
Postgres + pgvector instead of Qdrant
filesystem object store instead of MinIO if needed
no ClickHouse
no local LLM
smaller embedding model
```

Large local/full profile:

```text
Qdrant enabled
ClickHouse enabled
MinIO enabled
local embedding service optional
worker concurrency configurable
```

## Implementation Order

1. Docker Compose with Postgres, Redis, MinIO, Qdrant, API, worker, web.
2. Alembic migrations and idempotent seed.
3. Module registry with bundled `site_audit`.
4. Website crawler and raw object storage.
5. Entity/content/metric creation for crawled pages.
6. Local embeddings and Qdrant indexing.
7. Site audit technical analysis.
8. Semantic clustering, outliers, duplicates, and internal link gaps.
9. GEO readiness scoring.
10. Site Audit UI and reports.
11. MCP resources and prompts for site audit.
12. Domain comparison workflow.
13. Optional ClickHouse profile for larger event/metric history.

## Key Design Decisions

- Local Docker is the first-class distribution, not an afterthought.
- Site Audit and GEO is the default bundled module.
- Postgres remains the source of truth.
- Qdrant is included in the default local stack for serious semantic search.
- pgvector remains available for minimal mode and tests.
- MinIO stores raw HTML, snapshots, artifacts, and reports.
- ClickHouse is optional until event/metric volume requires it.
- Modules should be configuration-first and migration-light.
- Paid modules should plug into the same module registry, not fork the core.
