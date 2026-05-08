# ruff: noqa: E501

"""Embedding metadata schema.

Revision ID: 0003_embedding_metadata_schema
Revises: 0002_ingestion_content_schema
Create Date: 2026-05-08
"""

from alembic import op

revision = "0003_embedding_metadata_schema"
down_revision = "0002_ingestion_content_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        create table if not exists embedding_models (
          id uuid primary key default gen_random_uuid(),
          provider text not null,
          model_name text not null,
          model_version text not null default 'default',
          dimension integer not null,
          distance_metric text not null default 'cosine',
          normalized boolean not null default true,
          capabilities_json jsonb not null default '{}'::jsonb,
          created_at timestamptz not null default now(),
          constraint uq_embedding_models_identity unique (provider, model_name, model_version)
        );

        create table if not exists embedding_runs (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          embedding_model_id uuid not null references embedding_models(id) on delete cascade,
          status text not null default 'queued',
          target_filter_json jsonb not null default '{}'::jsonb,
          started_at timestamptz,
          finished_at timestamptz,
          error_message text,
          created_at timestamptz not null default now()
        );

        create table if not exists embeddings (
          id uuid primary key default gen_random_uuid(),
          tenant_id uuid not null references tenants(id) on delete cascade,
          workspace_id uuid not null references workspaces(id) on delete cascade,
          dataset_id uuid not null references datasets(id) on delete cascade,
          embedding_run_id uuid references embedding_runs(id),
          entity_id uuid references entities(id) on delete cascade,
          content_unit_id uuid references content_units(id) on delete cascade,
          content_chunk_id uuid references content_chunks(id) on delete cascade,
          embedding_model_id uuid not null references embedding_models(id) on delete cascade,
          vector_store text not null,
          vector_collection text not null,
          vector_point_id text not null,
          content_hash text not null,
          embedding_status text not null default 'ready',
          created_at timestamptz not null default now(),
          constraint uq_embeddings_vector_point unique (
            embedding_model_id,
            vector_store,
            vector_collection,
            vector_point_id
          )
        );

        create index if not exists ix_embedding_runs_dataset on embedding_runs(dataset_id);
        create index if not exists ix_embeddings_dataset_chunk on embeddings(dataset_id, content_chunk_id);
        create index if not exists ix_embeddings_vector_collection on embeddings(vector_store, vector_collection);
        """
    )


def downgrade() -> None:
    for table in (
        "embeddings",
        "embedding_runs",
        "embedding_models",
    ):
        op.execute(f"drop table if exists {table} cascade")
