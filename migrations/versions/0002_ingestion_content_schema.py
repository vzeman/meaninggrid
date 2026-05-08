# ruff: noqa: E501

"""Ingestion and content schema.

Revision ID: 0002_ingestion_content_schema
Revises: 0001_core_local_schema
Create Date: 2026-05-08
"""

from alembic import op

revision = "0002_ingestion_content_schema"
down_revision = "0001_core_local_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        create table if not exists raw_objects (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          source_id uuid not null references sources(id) on delete cascade,
          external_id text,
          object_kind text not null,
          object_uri text not null,
          content_hash text not null,
          mime_type text,
          size_bytes bigint,
          captured_at timestamptz not null default now(),
          source_updated_at timestamptz,
          metadata_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now(),
          constraint uq_raw_objects_source_external_hash unique (source_id, external_id, content_hash)
        );

        create table if not exists source_events (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          source_id uuid not null references sources(id) on delete cascade,
          data_stream_id uuid references data_streams(id) on delete set null,
          external_event_id text,
          event_type text not null,
          occurred_at timestamptz,
          received_at timestamptz not null default now(),
          source_updated_at timestamptz,
          raw_object_id uuid references raw_objects(id) on delete set null,
          idempotency_key text not null,
          payload_hash text,
          processing_status text not null default 'pending',
          partition_key text,
          sequence text,
          priority_hint text,
          route_hint text,
          metadata_json jsonb not null default '{}'::jsonb,
          labels_json jsonb not null default '{}'::jsonb,
          classification_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now(),
          constraint uq_source_events_idempotency unique (tenant_id, idempotency_key)
        );

        create table if not exists entities (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          entity_type_id uuid not null references entity_types(id) on delete cascade,
          external_id text,
          label text not null,
          description text,
          canonical_uri text,
          raw_object_id uuid references raw_objects(id) on delete set null,
          properties_json jsonb not null default '{}'::jsonb,
          labels_json jsonb not null default '{}'::jsonb,
          classification_json jsonb not null default '{}'::jsonb,
          source_created_at timestamptz,
          source_updated_at timestamptz,
          created_at timestamptz not null default now(),
          updated_at timestamptz,
          constraint uq_entities_dataset_type_external unique (dataset_id, entity_type_id, external_id)
        );

        create table if not exists content_units (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          entity_id uuid references entities(id) on delete cascade,
          raw_object_id uuid references raw_objects(id) on delete set null,
          unit_kind text not null,
          title text,
          text text,
          language text,
          order_index integer,
          token_count integer,
          word_count integer,
          content_hash text not null,
          metadata_json jsonb not null default '{}'::jsonb,
          labels_json jsonb not null default '{}'::jsonb,
          classification_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now(),
          constraint uq_content_units_identity unique (dataset_id, entity_id, unit_kind, order_index, content_hash)
        );

        create table if not exists entity_relations (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          from_entity_id uuid not null references entities(id) on delete cascade,
          to_entity_id uuid references entities(id) on delete set null,
          to_external_ref text,
          relation_type text not null,
          weight double precision,
          confidence double precision,
          evidence_content_unit_id uuid references content_units(id),
          properties_json jsonb not null default '{}'::jsonb,
          labels_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now()
        );

        create table if not exists content_chunks (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          content_unit_id uuid not null references content_units(id) on delete cascade,
          entity_id uuid references entities(id) on delete cascade,
          chunk_index integer not null,
          text text not null,
          token_count integer,
          content_hash text not null,
          chunking_strategy text not null,
          chunking_version text not null,
          start_offset integer,
          end_offset integer,
          metadata_json jsonb not null default '{}'::jsonb,
          labels_json jsonb not null default '{}'::jsonb,
          classification_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now(),
          constraint uq_content_chunks_identity unique (content_unit_id, chunk_index, chunking_strategy, chunking_version)
        );

        create table if not exists metric_values (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          metric_definition_id uuid not null references metric_definitions(id) on delete cascade,
          entity_id uuid references entities(id) on delete cascade,
          content_unit_id uuid references content_units(id) on delete cascade,
          value_number double precision,
          value_text text,
          value_bool boolean,
          value_json jsonb,
          observed_at timestamptz not null default now(),
          valid_from timestamptz,
          valid_to timestamptz,
          aggregation_window text,
          dimensions_json jsonb not null default '{}'::jsonb,
          labels_json jsonb not null default '{}'::jsonb,
          source_id uuid references sources(id) on delete set null,
          source_event_id uuid references source_events(id) on delete set null,
          confidence double precision,
          created_at timestamptz not null default now()
        );

        create index if not exists ix_raw_objects_dataset on raw_objects(dataset_id);
        create index if not exists ix_source_events_dataset on source_events(dataset_id);
        create index if not exists ix_entities_dataset_type on entities(dataset_id, entity_type_id);
        create index if not exists ix_content_units_dataset_entity on content_units(dataset_id, entity_id);
        create index if not exists ix_content_chunks_dataset_entity on content_chunks(dataset_id, entity_id);
        create index if not exists ix_entity_relations_dataset_from on entity_relations(dataset_id, from_entity_id);
        create index if not exists ix_metric_values_dataset_entity on metric_values(dataset_id, entity_id);
        """
    )


def downgrade() -> None:
    for table in (
        "metric_values",
        "content_chunks",
        "entity_relations",
        "content_units",
        "entities",
        "source_events",
        "raw_objects",
    ):
        op.execute(f"drop table if exists {table} cascade")
