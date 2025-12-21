.PHONY: help run lint lint-fix format check install test clean

# Variables
PYTHON := python3
UV := uv
APP_MODULE := wsgi:app
HOST := 0.0.0.0
PORT := 8000
WORKERS := $(or $(word 2, $(MAKECMDGOALS)), 4)
TIMEOUT := 120

ifneq ($(filter-out run run-dev,$(MAKECMDGOALS)),)
  $(filter-out run run-dev,$(MAKECMDGOALS)):
	@:
endif

help: 
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:
	$(UV) sync --extra dev

install-prod:
	$(UV) sync

run:
	$(UV) run gunicorn $(APP_MODULE) \
		--bind $(HOST):$(PORT) \
		--workers $(WORKERS) \
		--timeout $(TIMEOUT) \
		--access-logfile - \
		--error-logfile - \
		--log-level info

run-dev:
	$(UV) run gunicorn $(APP_MODULE) \
		--bind $(HOST):$(PORT) \
		--workers $(WORKERS) \
		--timeout $(TIMEOUT) \
		--reload \
		--access-logfile - \
		--error-logfile - \
		--log-level debug

lint:
	$(UV) run ruff check .

lint-fix:
	$(UV) run ruff check --fix .

format:
	$(UV) run ruff format .

check: lint
	@echo "All checks passed!"

test:
	$(UV) run pytest

test-cov:
	$(UV) run pytest --cov=songs_api --cov-report=html --cov-report=term

init-db:
	$(UV) run python -m songs_api.scripts.init_db

seed-songs:
	$(UV) run python -m songs_api.scripts.seed

seed-users:
	$(UV) run python -m songs_api.scripts.seed_users

seed: init-db seed-songs seed-users

clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov dist build

