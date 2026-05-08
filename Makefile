PYTHON ?= python3

.PHONY: up down logs ps backend-shell web-shell lint test format

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

backend-shell:
	docker compose run --rm api bash

web-shell:
	docker compose run --rm web sh

lint:
	$(PYTHON) -m ruff check apps packages || true
	pnpm --filter @meaninggrid/web typecheck || true

test:
	$(PYTHON) -m pytest || true
	pnpm --filter @meaninggrid/web test || true

format:
	$(PYTHON) -m ruff format apps packages || true
