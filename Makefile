.PHONY: setup install lint test format run docker clean coverage pre-commit help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Create venv and install all dependencies
	uv venv && . .venv/bin/activate && uv pip install -e .[dev]

install:  ## Install dependencies only
	uv pip install -e .[dev]

lint:  ## Run linting and type checking
	ruff check . && mypy src --ignore-missing-imports

format:  ## Format code with ruff, black, and isort
	ruff check . --fix && ruff format . && isort . && black .

test:  ## Run tests with fail-fast
	pytest -q --maxfail=1

test-v:  ## Run tests with verbose output
	pytest -v

test-cov:  ## Run tests with coverage report
	pytest -v --cov=src --cov-report=term-missing --cov-report=html

coverage:  ## Open coverage report in browser
	open htmlcov/index.html

run:  ## Run development server with reload
	uv run uvicorn src.app:app --reload --port 8000

docker:  ## Build Docker image locally
	docker build -t ghcr.io/${USER}/ticket-triage-agent:local .

docker-run:  ## Run Docker container locally
	docker run -p 8000:8000 ghcr.io/${USER}/ticket-triage-agent:local

pre-commit:  ## Install pre-commit hooks
	pre-commit install

pre-commit-run:  ## Run pre-commit on all files
	pre-commit run --all-files

clean:  ## Clean up build artifacts and cache
	rm -rf .venv .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
