# Migrations

MeaningGrid uses Alembic for Postgres schema migrations.

The first migration sequence is specified in:

```text
docs/23-initial-database-schema-v0.md
```

Local Docker runs migrations and the idempotent local seed through the
`migrate` service before the API starts:

```bash
docker compose run --rm migrate
```

The first revision creates the local v0 identity, module, dataset, source,
schema registry, and job tables.
