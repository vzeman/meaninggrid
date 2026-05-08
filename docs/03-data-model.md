# Data Model

## Design Goal

MeaningGrid needs one internal model that can represent websites, companies,
branches, support tickets, calls, documents, spreadsheets, and custom business
objects.

The model should separate:

- raw source data
- normalized entities
- text/content units
- chunks
- metrics
- relationships
- embeddings
- analysis artifacts
- insights and evidence
- agent context

Implementation-level table-family and local schema guidance:
[Local Docker Infrastructure And Flexible Schema](20-local-docker-infrastructure-and-flexible-schema.md).

## Core Object Hierarchy

```text
Tenant
  Workspace
    Dataset
      Source
        DataStream
          SourceEvent
            EventRoute
        RawObject
      EntityType
        Entity
          EntityVersion
          ContentUnit
            ContentChunk
          MetricValue
      EntityRelation
      EntityChangeEvent
      ContextUnit
        ContextResourceVersion
      AgentSubscription
        ContextNotification
      AnalysisRun
        AnalysisArtifact
        Insight
          Evidence
      ContextPack
      SharedMemoryItem
```

## Main Tables

### tenants

Represents a customer, organization, or local installation owner.

Fields:

- id
- name
- slug
- plan
- created_at
- updated_at

### label_definitions

Optional workspace-level registry of known labels.

Fields:

- id
- tenant_id
- workspace_id
- key
- display_name
- description
- value_type
- allowed_values_json
- protected
- created_at
- updated_at

Labels may still be schemaless in early MVP, but a registry helps prevent
label drift in larger deployments.

### workspaces

Represents a business area, team, client, or project grouping.

Fields:

- id
- tenant_id
- name
- slug
- description
- default_language
- labels_json
- created_by_user_id
- created_at
- updated_at

### agent_sessions

Represents a headless AI-agent session.

Fields:

- id
- tenant_id
- workspace_id
- actor_user_id
- service_account_id
- agent_id
- client_name
- purpose
- allowed_tools_json
- policy_id
- started_at
- expires_at
- metadata_json

Identity modes:

```text
user-delegated
service-account
workspace-agent
tenant-agent
anonymous-local
```

### agent_subscriptions

Represents a long-running agent subscription to MeaningGrid context changes.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- agent_session_id
- name
- resource_uri
- filters_json
- semantic_interest
- priority_min
- delivery_mode
- context_budget_tokens
- status
- last_sequence
- replay_window_seconds
- created_at
- updated_at
- expires_at

delivery_mode examples:

```text
notify_then_pull
inline_small_event
daily_digest
context_unit_only
manual_poll_only
```

### context_notifications

Durable notification log for context updates delivered to agents.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- agent_subscription_id
- context_unit_id
- source_event_id
- event_route_id
- resource_uri
- notification_type
- sequence
- partition_key
- priority
- summary
- status
- delivered_at
- acknowledged_at
- verdict
- error_message
- created_at

status examples:

```text
pending
delivered
acknowledged
expired
failed
```

### modules

Represents an installed module package.

Fields:

- id
- module_key
- name
- description
- current_version
- status
- installed_at
- updated_at

### module_installations

Represents module enablement in a tenant or workspace.

Fields:

- id
- tenant_id
- workspace_id
- module_id
- module_version
- enabled
- config_json
- installed_by_user_id
- installed_at

### module_resources

Represents resources registered by a module.

Fields:

- id
- module_installation_id
- resource_type
- resource_key
- resource_version
- config_json
- status
- created_at

resource_type examples:

```text
entity_schema
connector
mapping_preset
analysis_preset
context_template
mcp_prompt
dashboard
report_template
monitor_template
```

### datasets

A dataset is an imported and analyzable collection.

Examples:

- one website crawl
- one call-center transcript import
- one company benchmark dataset
- one support-ticket sync

Fields:

- id
- tenant_id
- workspace_id
- name
- description
- dataset_kind
- status
- source_count
- entity_count
- content_unit_count
- freshness_at
- labels_json
- classification_json
- created_at
- updated_at

dataset_kind examples:

```text
website
company_benchmark
call_center
support_tickets
knowledge_base
spreadsheet
custom
```

### sources

Represents a connector instance or upload source.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- connector_type
- connector_version
- display_name
- labels_json
- classification_json
- config_ref
- sync_state
- last_sync_at
- created_at
- updated_at

connector_type examples:

```text
website_crawler
csv_upload
xlsx_upload
postgres
mysql
zendesk
liveagent
salesforce
hubspot
intercom
slack
google_drive
api_webhook
```

### data_streams

Represents a continuous or repeatable stream of source data.

Examples:

- Google Search Console daily metrics
- Google Ads campaign metrics
- Meta/Facebook Ads campaign metrics
- ecommerce orders webhook
- support tickets incremental sync
- call transcript arrivals
- investor deal-flow pipeline

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- source_id
- name
- stream_type
- sync_mode
- status
- cursor_json
- watermark_at
- labels_json
- classification_json
- schedule_cron
- created_at
- updated_at

sync_mode examples:

```text
batch
periodic
webhook
stream
cdc
```

### source_events

Append-only record of source changes. This is the foundation for replay,
backfill, deduplication, and reprocessing.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- source_id
- data_stream_id
- external_event_id
- event_type
- occurred_at
- received_at
- source_updated_at
- raw_object_id
- idempotency_key
- payload_hash
- processing_status
- metadata_json
- labels_json
- classification_json

event_type examples:

```text
created
updated
deleted
metric_observed
snapshot_observed
relationship_changed
content_changed
```

### event_routes

Stores the routing decision for a source event. This is used by the Streaming
Agent Context Engine to decide whether an event should notify agents
immediately, join a batch context unit, be archived only, or be ignored as
noise.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- source_event_id
- route
- priority
- urgency_score
- confidence
- reason
- rule_id
- classifier_name
- classifier_version
- feature_snapshot_json
- memory_scope
- ttl_seconds
- decided_at
- feedback_status
- created_at

route examples:

```text
fast
batch
fast_and_batch
archive_only
drop_noise
manual_review
```

priority examples:

```text
p0
p1
p2
p3
```

### raw_objects

Stores immutable references to imported source payloads.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- source_id
- external_id
- object_kind
- object_uri
- content_hash
- mime_type
- size_bytes
- captured_at
- source_updated_at
- metadata_json

Raw payloads should live in object storage. The database keeps references and
hashes.

### entity_types

Defines the logical entity schema for a dataset.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- name
- display_name
- description
- schema_json
- primary_label_field
- default_text_fields
- created_at
- updated_at

Examples:

```text
domain
page
paragraph
company
branch
person
call
ticket
document
product
review
```

### entities

Represents normalized objects.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- entity_type_id
- external_id
- label
- description
- canonical_uri
- raw_object_id
- properties_json
- labels_json
- classification_json
- source_created_at
- source_updated_at
- created_at
- updated_at

Important:

- properties_json stores connector-specific attributes.
- commonly queried fields should be promoted later.
- entities should be versioned through import snapshots when needed.

### entity_versions

Stores historical entity state when versioning is enabled.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- entity_id
- version_number
- valid_from
- valid_to
- content_hash
- properties_json
- source_event_id
- created_at

### entity_change_events

Normalized change log derived from source events.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- source_event_id
- entity_id
- entity_type_id
- change_type
- valid_from
- valid_to
- properties_patch_json
- content_changed
- metrics_changed
- relations_changed
- created_at

change_type examples:

```text
upsert
delete
restore
metric_update
relation_update
content_update
```

### entity_relations

Represents graph edges between entities.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- from_entity_id
- to_entity_id
- relation_type
- weight
- confidence
- evidence_content_unit_id
- properties_json
- labels_json
- created_at

relation_type examples:

```text
belongs_to
owns
links_to
works_for
handled_by
replied_to
mentions
located_in
similar_to
derived_from
competes_with
```

### content_units

Represents a semantically meaningful text-bearing unit.

Examples:

- page body
- paragraph
- heading
- transcript
- speaker turn
- ticket message
- review
- document section

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- entity_id
- raw_object_id
- unit_kind
- title
- text
- language
- order_index
- token_count
- word_count
- content_hash
- metadata_json
- labels_json
- classification_json
- created_at

unit_kind examples:

```text
page_body
paragraph
heading
transcript
transcript_turn
email
ticket_message
review
document_section
spreadsheet_row
```

### content_chunks

Represents embedding-sized segments.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- content_unit_id
- entity_id
- chunk_index
- text
- token_count
- content_hash
- chunking_strategy
- chunking_version
- start_offset
- end_offset
- metadata_json
- labels_json
- classification_json
- created_at

### context_units

Represents a durable, agent-readable unit of live or aggregated context.

Examples:

- support ticket timeline
- trial account journey
- customer session rollup
- campaign daily alignment
- startup dossier
- contract obligation timeline
- audit evidence window

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- context_unit_type
- entity_id
- target_type
- target_id
- title
- summary
- facts_json
- metrics_json
- source_event_ids_json
- raw_object_ids_json
- valid_from
- valid_to
- watermark_at
- version_number
- token_count
- compression_ratio
- confidence
- labels_json
- classification_json
- access_policy_id
- created_at
- updated_at

Context units are derived, but they should be first-class because agents need
stable resource URIs, versioning, evidence links, and subscription semantics.

### context_resource_versions

Tracks versioned context resources that can notify agents when they change.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- resource_uri
- resource_type
- target_type
- target_id
- context_unit_id
- sequence
- partition_key
- content_hash
- produced_from_event_id
- produced_from_artifact_id
- watermark_at
- created_at

resource_type examples:

```text
context_stream
context_unit
entity_profile
dataset_card
shared_memory_item
context_pack
```

### metric_definitions

Defines structured measures.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- name
- display_name
- description
- value_type
- unit
- direction
- aggregation
- properties_json
- labels_json

direction examples:

```text
higher_is_better
lower_is_better
neutral
```

metric examples:

```text
sale_closed
conversion_rate
revenue
csat
sentiment_score
traffic
impressions
rank
duration
resolution_time
```

### metric_values

Stores values attached to entities, content units, or analysis windows.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- metric_definition_id
- entity_id
- content_unit_id
- value_number
- value_text
- value_bool
- value_json
- observed_at
- valid_from
- valid_to
- aggregation_window
- dimensions_json
- labels_json
- source_id
- source_event_id
- confidence

Metric dimensions are important for marketing and operational streams.

Examples:

```text
country
device
campaign
ad_group
keyword
query
page
product
channel
source
```

### embedding_models

Tracks vector space identity.

Fields:

- id
- provider
- model_name
- model_version
- dimension
- distance_metric
- normalized
- capabilities_json
- created_at

### embeddings

Stores vector metadata and points to vector storage.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- entity_id
- content_unit_id
- content_chunk_id
- embedding_model_id
- vector_store
- vector_collection
- vector_point_id
- content_hash
- embedding_status
- created_at

Rules:

- Never compare vectors from incompatible embedding_model_id values.
- Always store content_hash and chunking_version.
- Re-embedding creates new records unless explicitly replacing a collection.
- Vector payloads should include tenant/workspace/dataset IDs, labels,
  classification, access policy, entity/content IDs, and timestamps.

### analysis_runs

Represents a reproducible analysis execution.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- analysis_type
- status
- input_spec_json
- code_version
- started_at
- finished_at
- created_by_user_id
- error_message

analysis_type examples:

```text
semantic_overview
website_geo_audit
cohort_comparison
call_center_analysis
support_ticket_analysis
entity_benchmark
context_index_refresh
```

### analysis_artifacts

Stores generated data artifacts from analysis runs.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- analysis_run_id
- artifact_type
- artifact_uri
- artifact_json
- content_hash
- created_at

artifact_type examples:

```text
cluster_summary
projection_2d
projection_3d
outlier_table
duplicate_pairs
cohort_diff
semantic_gap_table
centroid_metrics
similarity_matrix_sample
report_html
```

### derivation_specs

Defines versioned ways to produce derived data.

Examples:

- chunking strategy
- embedding model
- metric extractor
- entity mapper
- clusterer
- sentiment model
- topic classifier
- summary prompt
- analysis template

Fields:

- id
- tenant_id
- workspace_id
- name
- spec_type
- version
- config_json
- code_version
- created_at

### derived_artifacts

Tracks derived outputs so they can be invalidated and regenerated.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- artifact_kind
- target_type
- target_id
- derivation_spec_id
- input_hash
- output_hash
- status
- created_at
- invalidated_at

### insights

Represents a human- or AI-readable finding.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- analysis_run_id
- title
- summary
- severity
- confidence
- insight_type
- affected_entity_count
- recommendation
- status
- created_at

insight_type examples:

```text
outlier
duplicate
cluster
gap
drift
cohort_difference
success_pattern
risk
opportunity
data_quality
```

### insight_evidence

Links insights to exact source material.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- insight_id
- entity_id
- content_unit_id
- content_chunk_id
- metric_value_id
- raw_object_id
- quote
- score
- explanation
- created_at

### context_packs

Represents an agent-readable bundle.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- task
- budget_tokens
- policy_id
- pack_json
- pack_uri
- created_by
- created_at
- expires_at

### shared_memory_items

Stores explicit, governed memory that agents and humans can inspect.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- scope
- target_type
- target_id
- memory_type
- title
- content
- facts_json
- source_event_ids_json
- context_unit_ids_json
- insight_id
- created_by_actor
- created_by_agent_session_id
- confidence
- labels_json
- classification_json
- access_policy_id
- valid_from
- valid_to
- expires_at
- supersedes_memory_item_id
- created_at
- updated_at

scope examples:

```text
private_agent
user_private
team_shared
workspace_shared
tenant_shared
module_shared
entity_scoped
```

memory_type examples:

```text
observation
summary
fact
decision
assumption
accepted_insight
rejected_insight
agent_note
human_feedback
playbook
policy
```

### routing_feedback

Stores feedback from agents or humans about event routing quality.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- source_event_id
- event_route_id
- context_notification_id
- agent_session_id
- verdict
- reason
- created_at

verdict examples:

```text
appropriate
too_urgent
too_slow
irrelevant
missing_context
wrong_recipient
useful_but_low_priority
```

### agent_notes

Stores durable labels, assumptions, decisions, and feedback.

Fields:

- id
- tenant_id
- workspace_id
- dataset_id
- entity_id
- analysis_run_id
- note_type
- body
- created_by
- created_at

note_type examples:

```text
label
assumption
decision
rejected_insight
accepted_recommendation
domain_context
```

## Example Mapping: Website

```text
EntityType: domain
EntityType: page
EntityType: paragraph
EntityType: heading
EntityType: link

domain -> page: owns
page -> paragraph: contains
page -> heading: contains
page -> page: links_to
```

Content units:

- page body
- paragraph text
- heading text
- anchor text

Metrics:

- word count
- internal links
- external links
- traffic
- impressions
- conversions
- answerability score

## Example Mapping: Call Center

```text
EntityType: call
EntityType: agent
EntityType: customer
EntityType: transcript_turn
EntityType: objection

call -> agent: handled_by
call -> customer: involves
transcript_turn -> call: belongs_to
objection -> call: detected_in
```

Content units:

- full transcript
- speaker turn
- call phase
- objection segment

Metrics:

- sale_closed
- duration
- sentiment
- talk ratio
- interruption count
- csat

## Example Mapping: Company Benchmark

```text
EntityType: company
EntityType: branch
EntityType: employee
EntityType: product
EntityType: review

company -> branch: owns
employee -> branch: works_for
review -> branch: describes
product -> company: belongs_to
```

Metrics:

- revenue
- growth
- customer satisfaction
- review rating
- retention
- conversion

## Versioning Strategy

Initial versioning:

- raw objects are immutable by content_hash
- source events are append-only and idempotent
- analysis runs are immutable
- embeddings are tied to model and content hash
- context packs are generated snapshots

Later enterprise versioning:

- dataset snapshots
- entity history
- relation history
- metric time series
- context pack retention policies

## Streaming And Reprocessing Strategy

Current state and history should both exist:

```text
current state: fast dashboards, current search, current context
history: temporal analysis, auditability, replay, reprocessing
```

Rules:

- preserve raw source events where retention policy allows it
- store idempotency keys for deduplication
- update current entity state for fast reads
- append entity change events for history
- invalidate derived artifacts when source content, metrics, or relations change
- keep derivation specs versioned
- reprocess historical data without overwriting old analysis runs by default
