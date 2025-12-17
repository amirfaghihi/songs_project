.PHONY: help run lint lint-fix format check install test clean

# Variables
PYTHON := python3
UV := uv
APP_MODULE := wsgi:app
HOST := 0.0.0.0
PORT := 8000
WORKERS := 4
TIMEOUT := 120

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (including dev) using uv
	$(UV) sync --extra dev

install-prod: ## Install production dependencies only
	$(UV) sync

run: ## Run the application with gunicorn
	$(UV) run gunicorn $(APP_MODULE) \
		--bind $(HOST):$(PORT) \
		--workers $(WORKERS) \
		--timeout $(TIMEOUT) \
		--access-logfile - \
		--error-logfile - \
		--log-level info

run-dev: ## Run the application with gunicorn in development mode (reload on changes)
	$(UV) run gunicorn $(APP_MODULE) \
		--bind $(HOST):$(PORT) \
		--workers 2 \
		--timeout $(TIMEOUT) \
		--reload \
		--access-logfile - \
		--error-logfile - \
		--log-level debug

lint: ## Run linting checks with ruff
	$(UV) run ruff check .

lint-fix: ## Run ruff check and auto-fix issues
	$(UV) run ruff check --fix .

format: ## Format code with ruff
	$(UV) run ruff format .

check: lint ## Run all checks (linting)
	@echo "All checks passed!"

test: ## Run tests with pytest
	$(UV) run pytest

test-cov: ## Run tests with coverage
	$(UV) run pytest --cov=songs_api --cov-report=html --cov-report=term

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov dist build

