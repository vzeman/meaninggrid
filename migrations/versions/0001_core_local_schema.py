# ruff: noqa: E501

"""Core local schema.

Revision ID: 0001_core_local_schema
Revises:
Create Date: 2026-05-08
"""

from alembic import op

revision = "0001_core_local_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create extension if not exists pgcrypto")
    op.execute("create extension if not exists vector")
    op.execute(
        """
        create table if not exists tenants (
          id uuid primary key default gen_random_uuid(),
          name text not null,
          slug text not null unique,
          plan text not null default 'local',
          created_at timestamptz not null default now(),
          updated_at timestamptz
        );

        create table if not exists users (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          email text not null,
          display_name text,
          role text not null default 'admin',
          password_hash text,
          is_local_admin boolean not null default false,
          created_at timestamptz not null default now(),
          updated_at timestamptz,
          constraint uq_users_tenant_email unique (tenant_id, email)
        );

        create table if not exists workspaces (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          name text not null,
          slug text not null,
          description text,
          default_language text,
          labels_json jsonb not null default '{}'::jsonb,
          created_by_user_id uuid references users(id) on delete set null,
          created_at timestamptz not null default now(),
          updated_at timestamptz,
          constraint uq_workspaces_tenant_slug unique (tenant_id, slug)
        );

        create table if not exists workspace_members (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          user_id uuid not null references users(id) on delete cascade,
          role text not null default 'owner',
          created_at timestamptz not null default now(),
          constraint uq_workspace_members_pair unique (workspace_id, user_id)
        );

        create table if not exists modules (
          id uuid primary key default gen_random_uuid(),
          module_key text not null unique,
          name text not null,
          description text,
          current_version text not null,
          bundled boolean not null default false,
          status text not null default 'active',
          created_at timestamptz not null default now(),
          updated_at timestamptz
        );

        create table if not exists module_installations (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid references workspaces(id) on delete cascade,
          module_id uuid not null references modules(id) on delete cascade,
          module_version text not null,
          enabled boolean not null default true,
          config_json jsonb not null default '{}'::jsonb,
          installed_by_user_id uuid references users(id) on delete set null,
          installed_at timestamptz not null default now(),
          constraint uq_module_installations_scope unique (tenant_id, workspace_id, module_id)
        );

        create table if not exists module_resources (
          id uuid primary key default gen_random_uuid(),
          module_installation_id uuid not null references module_installations(id) on delete cascade,
          resource_type text not null,
          resource_key text not null,
          resource_version text not null default '1',
          config_json jsonb not null default '{}'::jsonb,
          status text not null default 'active',
          created_at timestamptz not null default now(),
          constraint uq_module_resources_installation_key
            unique (module_installation_id, resource_type, resource_key)
        );

        create table if not exists label_definitions (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid references workspaces(id) on delete cascade,
          key text not null,
          display_name text,
          description text,
          value_type text not null default 'string',
          allowed_values_json jsonb,
          protected boolean not null default false,
          created_at timestamptz not null default now(),
          updated_at timestamptz,
          constraint uq_label_definitions_scope_key unique (tenant_id, workspace_id, key)
        );

        create table if not exists datasets (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          name text not null,
          slug text,
          description text,
          dataset_kind text not null,
          status text not null default 'draft',
          source_count integer not null default 0,
          entity_count integer not null default 0,
          content_unit_count integer not null default 0,
          freshness_at timestamptz,
          labels_json jsonb not null default '{}'::jsonb,
          classification_json jsonb not null default '{}'::jsonb,
          created_by_user_id uuid references users(id) on delete set null,
          created_at timestamptz not null default now(),
          updated_at timestamptz
        );

        create table if not exists sources (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          connector_type text not null,
          connector_version text,
          display_name text not null,
          labels_json jsonb not null default '{}'::jsonb,
          classification_json jsonb not null default '{}'::jsonb,
          config_json jsonb not null default '{}'::jsonb,
          sync_state_json jsonb not null default '{}'::jsonb,
          last_sync_at timestamptz,
          created_at timestamptz not null default now(),
          updated_at timestamptz
        );

        create table if not exists data_streams (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          source_id uuid not null references sources(id) on delete cascade,
          name text not null,
          stream_type text not null,
          sync_mode text not null,
          status text not null default 'active',
          cursor_json jsonb not null default '{}'::jsonb,
          watermark_at timestamptz,
          labels_json jsonb not null default '{}'::jsonb,
          classification_json jsonb not null default '{}'::jsonb,
          schedule_cron text,
          created_at timestamptz not null default now(),
          updated_at timestamptz
        );

        create table if not exists entity_types (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid references datasets(id) on delete cascade,
          module_key text,
          name text not null,
          display_name text not null,
          description text,
          schema_json jsonb not null default '{}'::jsonb,
          primary_label_field text,
          default_text_fields jsonb not null default '[]'::jsonb,
          created_at timestamptz not null default now(),
          updated_at timestamptz,
          constraint uq_entity_types_scope_name unique (tenant_id, workspace_id, dataset_id, name)
        );

        create table if not exists relation_definitions (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid references datasets(id) on delete cascade,
          module_key text,
          name text not null,
          display_name text not null,
          description text,
          from_entity_type text,
          to_entity_type text,
          properties_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now(),
          constraint uq_relation_definitions_scope_name
            unique (tenant_id, workspace_id, dataset_id, name)
        );

        create table if not exists metric_definitions (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid references datasets(id) on delete cascade,
          module_key text,
          name text not null,
          display_name text not null,
          description text,
          value_type text not null,
          unit text,
          direction text not null default 'neutral',
          aggregation text,
          properties_json jsonb not null default '{}'::jsonb,
          labels_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now(),
          updated_at timestamptz,
          constraint uq_metric_definitions_scope_name unique (tenant_id, workspace_id, dataset_id, name)
        );

        create table if not exists jobs (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid references datasets(id) on delete cascade,
          source_id uuid references sources(id) on delete set null,
          job_type text not null,
          status text not null default 'queued',
          progress_current integer not null default 0,
          progress_total integer,
          progress_message text,
          payload_json jsonb not null default '{}'::jsonb,
          result_json jsonb not null default '{}'::jsonb,
          error_json jsonb,
          created_by_user_id uuid references users(id) on delete set null,
          queued_at timestamptz not null default now(),
          started_at timestamptz,
          finished_at timestamptz,
          created_at timestamptz not null default now(),
          updated_at timestamptz
        );

        create table if not exists job_events (
          id uuid primary key default gen_random_uuid(),
          job_id uuid not null references jobs(id) on delete cascade,
          event_type text not null,
          message text,
          progress_current integer,
          progress_total integer,
          payload_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now()
        );

        create index if not exists ix_datasets_workspace_kind on datasets(workspace_id, dataset_kind);
        create index if not exists ix_sources_dataset on sources(dataset_id);
        create index if not exists ix_data_streams_source on data_streams(source_id);
        create index if not exists ix_jobs_status on jobs(status);
        create index if not exists ix_jobs_dataset on jobs(dataset_id);
        create index if not exists ix_job_events_job on job_events(job_id);
        """
    )


def downgrade() -> None:
    for table in (
        "job_events",
        "jobs",
        "metric_definitions",
        "relation_definitions",
        "entity_types",
        "data_streams",
        "sources",
        "datasets",
        "label_definitions",
        "module_resources",
        "module_installations",
        "modules",
        "workspace_members",
        "workspaces",
        "users",
        "tenants",
    ):
        op.execute(f"drop table if exists {table} cascade")
