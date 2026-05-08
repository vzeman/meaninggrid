# Storage And Infrastructure

## Storage Roles

MeaningGrid should use each storage system for its strength.

Detailed local-first Docker and schema plan:
[Local Docker Infrastructure And Flexible Schema](20-local-docker-infrastructure-and-flexible-schema.md).

```text
Postgres: source of truth
pgvector: local/simple vector search
Qdrant: main vector database for larger installs
ClickHouse: high-volume analytics and event history
Object storage: raw payloads, artifacts, exports
Redis/queue: jobs, caching, short-lived state
Event bus: streaming ingestion and change processing
```

## Postgres

Use Postgres for:

- tenants
- users
- workspaces
- datasets
- sources
- data streams
- source event metadata
- entity change events
- entity versions
- entity model
- content metadata
- metric definitions
- metric values for normal scale
- embedding metadata
- analysis runs
- insights
- evidence links
- context pack metadata
- audit log metadata

Use JSONB where flexibility matters, but promote fields that become common
filters.

## pgvector

Use pgvector for:

- MVP
- standalone mode
- small and medium datasets
- simple installations
- tests
- fallback vector store

Pros:

- simple operations
- transactional metadata and vectors together
- good enough for local developer experience
- supports approximate indexes

Cons:

- less specialized than Qdrant for large vector workloads
- can become harder to scale independently

Recommendation:

```text
Start with pgvector support, but design a VectorStore interface from day one.
Use Qdrant as the preferred scalable vector store.
```

## Qdrant

Use Qdrant for:

- SaaS vector search
- larger standalone installs
- high-cardinality filters
- payload filtering
- hybrid retrieval
- snapshots
- multi-collection strategies

Collection strategies:

### Shared Collection Per Model

```text
mg_{embedding_model_slug}_{content_kind}
```

Payload:

```json
{
  "tenant_id": "t_1",
  "workspace_id": "ws_1",
  "dataset_id": "ds_1",
  "entity_type": "page",
  "entity_id": "ent_1",
  "content_unit_id": "cu_1",
  "content_chunk_id": "cc_1",
  "language": "en",
  "access_policy_id": "pol_1"
}
```

Pros:

- fewer collections
- easier model-level search
- good for SaaS if filters are always applied

Cons:

- strict permission filters are critical
- noisy tenants can affect performance

### Collection Per Tenant

```text
tenant_{tenant_id}_{embedding_model_slug}_{content_kind}
```

Pros:

- stronger isolation
- easier enterprise export/delete
- predictable per-tenant performance

Cons:

- more collections
- more operational overhead

Recommendation:

- community/local: one collection per model/content kind
- SaaS small tenants: shared collections with strict filters
- enterprise: tenant-specific collections

## ClickHouse

Use ClickHouse for:

- event analytics
- audit event exploration
- source event history at high volume
- metric time series
- marketing performance time series
- usage analytics
- high-volume connector sync logs
- dashboard aggregations
- cost tracking
- large interaction histories

Do not make ClickHouse the first source of truth.

Potential future use:

- vector similarity for analytical workloads
- historical vector analysis
- large metric/cohort aggregations

## Object Storage

Use S3-compatible object storage for:

- raw imported payloads
- raw source events
- website HTML snapshots
- transcripts
- PDFs
- spreadsheet uploads
- generated reports
- large analysis artifacts
- projection files
- export bundles
- backup snapshots

Providers:

```text
AWS: S3
Azure: Blob Storage adapter
GCP: Cloud Storage adapter
Standalone: MinIO
```

Use an ObjectStore interface:

```text
put_object(uri, bytes, metadata)
get_object(uri)
delete_object(uri)
sign_url(uri, policy)
list_prefix(prefix)
```

## Queue And Workflow

MVP:

```text
Redis + Celery
```

Later:

```text
Temporal
```

Job types:

- connector sync
- stream event processing
- webhook processing
- file parse
- crawl
- normalize
- chunk
- embed
- analyze
- generate insight
- build context index
- export report
- delete dataset
- backfill
- reprocess derived artifacts
- route context event
- build context unit
- deliver context notification

Every job should have:

- id
- tenant_id
- workspace_id
- dataset_id
- type
- status
- retry count
- started_at
- finished_at
- logs
- error

## Event Bus And Streaming Context

The EventBus abstraction should support both ingestion workers and the
Streaming Agent Context Engine.

MVP:

```text
Redis streams or Celery queues
```

Enterprise:

```text
Redpanda
Kafka
NATS JetStream
AWS Kinesis
Google Pub/Sub
Azure Event Hubs
```

Required concepts:

- topic or stream name
- partition key
- sequence or offset
- at-least-once delivery
- idempotent consumers
- dead-letter queue
- replay window
- priority or priority emulation

Agent-facing subscriptions should not expose this bus directly. MeaningGrid
converts bus events into context resource versions and MCP/API notifications.

## Hot Context Store

Hot context views are low-latency projections for agents.

Initial options:

- Postgres current-state tables for simplicity
- Redis for short-lived hot state
- ClickHouse materialized views for high-volume event metrics
- Qdrant or pgvector for newest context unit embeddings

Durable truth remains:

```text
source_events + raw_objects + entity history + derived artifacts
```

## Cloud Replacement Matrix

| Capability | AWS | Azure | GCP | Standalone |
|---|---|---|---|---|
| Containers | EKS/ECS | AKS | GKE/Cloud Run | Docker/K3s |
| Postgres | RDS/Aurora | Azure Database for PostgreSQL | Cloud SQL | Postgres/CloudNativePG |
| Vector DB | Qdrant | Qdrant | Qdrant | Qdrant |
| Object storage | S3 | Blob Storage | Cloud Storage | MinIO |
| Queue | SQS/SNS or Redis | Service Bus or Redis | Pub/Sub or Redis | Redis/NATS |
| Event streaming | Kinesis/MSK | Event Hubs | Pub/Sub | Kafka/Redpanda/NATS |
| Analytics | ClickHouse | ClickHouse | ClickHouse | ClickHouse |
| Secrets | Secrets Manager | Key Vault | Secret Manager | Vault/SOPS |
| LLM | Bedrock | Azure AI Foundry | Vertex AI | vLLM/Ollama |
| Logs | CloudWatch | Azure Monitor | Cloud Logging | OpenTelemetry stack |

## LLM Provider Abstraction

MeaningGrid should support provider replacement:

```text
BedrockProvider
VertexProvider
AzureFoundryProvider
AnthropicProvider
OpenAIProvider
MistralProvider
CohereProvider
LocalProvider
```

Interface:

```text
chat(messages, options)
stream(messages, options)
extract_json(messages, schema, options)
summarize(input, options)
```

Embedding provider interface:

```text
embed(texts, model, options)
dimension(model)
token_limit(model)
```

Reranker provider interface:

```text
rerank(query, documents, options)
```

## Infrastructure As Code

Open-source:

- Docker Compose
- Helm chart

Enterprise:

- Helm chart with values files
- Terraform modules
- optional Pulumi later

Initial deployment folders:

```text
deployments/
  docker-compose/
  helm/
  terraform/
    aws/
    azure/
    gcp/
```

## Observability

Required:

- structured logs
- request IDs
- job IDs
- tenant IDs in logs where safe
- metrics for queue length, job time, errors
- tracing for API and workers
- vector search latency
- embedding cost
- LLM cost
- connector sync success/failure

Recommended:

- OpenTelemetry
- Prometheus
- Grafana
- Loki or cloud-native logs

## Backup And Restore

Backup:

- Postgres database
- Qdrant snapshots
- object storage raw/artifacts
- source event logs
- ClickHouse if enabled
- secrets configuration separately

Restore requirements:

- restore tenant
- restore workspace
- restore dataset
- restore full instance

Enterprise requirement:

- tested restore process
- documented RPO/RTO

## Local Offline Mode

Offline mode should support:

- no external APIs
- local embeddings
- local LLM optional
- local object storage
- local vector DB
- no telemetry by default

This is important for banks, healthcare, government, defense, and regulated
companies.

## Headless Mode

Headless mode should run without the web app.

Required services:

- API
- worker
- MCP server
- Postgres
- vector store
- Redis/event bus
- object storage

Optional services:

- ClickHouse
- local LLM
- local embedding server
- web dashboard

Docker Compose profiles:

```text
default
minimal
headless
analytics
local-ai
```

## Event Bus Interface

Streaming support should use an EventBus interface:

```text
publish(topic, event)
subscribe(topic, handler)
ack(event)
retry(event)
dead_letter(event)
```

Initial implementations:

- Redis streams or Celery queues for local mode
- Kafka/Redpanda for enterprise streaming
- cloud-native adapters later

Processing guarantee:

```text
at-least-once processing with idempotent writes
```
