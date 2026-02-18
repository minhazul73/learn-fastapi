# ───────────────────────────────────────────────────────────
# Makefile – common commands for dev & deployment
# ───────────────────────────────────────────────────────────
.PHONY: help dev prod migrate test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Local development ─────────────────────────────────────
dev: ## Run local dev server with reload
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ── Docker ────────────────────────────────────────────────
up-dev: ## Start dev containers
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

up-prod: ## Start prod containers (Oracle free tier tuned)
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

down: ## Stop all containers
	docker compose down

logs: ## Tail container logs
	docker compose logs -f app

# ── Database ──────────────────────────────────────────────
migrate: ## Generate a new migration
	alembic revision --autogenerate -m "$(msg)"

upgrade: ## Apply all pending migrations
	alembic upgrade head

downgrade: ## Rollback last migration
	alembic downgrade -1

# ── Quality ───────────────────────────────────────────────
lint: ## Run ruff linter + formatter check
	ruff check . && ruff format --check .

format: ## Auto-format code
	ruff format .

test: ## Run test suite
	pytest -v --tb=short

# ── Cleanup ───────────────────────────────────────────────
clean: ## Remove caches & build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name "*.pyc" -delete 2>/dev/null; true
	rm -rf .pytest_cache .ruff_cache
