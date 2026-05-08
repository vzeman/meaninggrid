PYTHON ?= python3

.PHONY: up down logs ps backend-shell web-shell migrate seed lint test smoke ready format

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

backend-shell:
	docker compose run --rm api sh

web-shell:
	docker compose run --rm web sh

migrate:
	docker compose run --rm migrate alembic -c migrations/alembic.ini upgrade head

seed:
	docker compose run --rm migrate python -m meaninggrid_db.seed

lint:
	docker compose run --rm --build test ruff check apps packages migrations scripts tests
	docker compose run --rm --no-deps --build web pnpm --filter @meaninggrid/web typecheck

test:
	docker compose run --rm --build test
	docker compose run --rm --no-deps --build web pnpm --filter @meaninggrid/web typecheck

smoke:
	docker compose run --rm --build test python scripts/site_audit_smoke.py

ready: lint test smoke

format:
	$(PYTHON) -m ruff format apps packages scripts tests || true
