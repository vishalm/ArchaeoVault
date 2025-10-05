.PHONY: help install install-dev test test-unit test-integration test-performance lint format type-check security-check coverage clean build docker-build docker-run docker-test docs serve-docs release pre-commit install-pre-commit update-deps

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	poetry install --only=main

install-dev: ## Install development dependencies
	poetry install --with dev

install-pre-commit: ## Install pre-commit hooks
	poetry run pre-commit install

# Testing
test: ## Run all tests
	poetry run pytest

test-unit: ## Run unit tests
	poetry run pytest tests/unit/ -v

test-integration: ## Run integration tests
	poetry run pytest tests/integration/ -v

test-performance: ## Run performance tests
	poetry run pytest tests/performance/ -v --benchmark-only

test-coverage: ## Run tests with coverage
	poetry run pytest --cov=app --cov-report=html --cov-report=xml --cov-report=term-missing

test-watch: ## Run tests in watch mode
	poetry run pytest-watch

# Code Quality
lint: ## Run all linting tools
	poetry run flake8 app/ tests/
	poetry run mypy app/ --ignore-missing-imports
	poetry run bandit -r app/ -f json -o bandit-report.json
	poetry run safety check
	poetry run xenon app/ --max-absolute B --max-average A

format: ## Format code
	poetry run black app/ tests/
	poetry run isort app/ tests/

format-check: ## Check code formatting
	poetry run black --check app/ tests/
	poetry run isort --check-only app/ tests/

type-check: ## Run type checking
	poetry run mypy app/ --ignore-missing-imports

# Security
security-check: ## Run security checks
	poetry run bandit -r app/ -f json -o bandit-report.json
	poetry run safety check --json --output safety-report.json
	poetry run pip-audit --format=json --output=pip-audit-report.json

security-fix: ## Fix security issues
	poetry run safety check --json --output safety-report.json
	poetry run pip-audit --format=json --output=pip-audit-report.json

# Coverage
coverage: ## Generate coverage report
	poetry run pytest --cov=app --cov-report=html --cov-report=xml --cov-report=term-missing

coverage-html: ## Open coverage report in browser
	open htmlcov/index.html

# Code Analysis
complexity: ## Check code complexity
	poetry run radon cc app/ --json --output radon-complexity.json
	poetry run xenon app/ --max-absolute B --max-average A

maintainability: ## Check code maintainability
	poetry run radon mi app/ --json --output radon-maintainability.json

dead-code: ## Find dead code
	poetry run vulture app/ --min-confidence 60 --exclude tests/

docstring-coverage: ## Check docstring coverage
	poetry run interrogate --config pyproject.toml

# Performance
profile: ## Profile application performance
	poetry run python -m memory_profiler app/main.py

benchmark: ## Run performance benchmarks
	poetry run pytest tests/performance/ --benchmark-only --benchmark-save=performance

# Documentation
docs: ## Generate documentation
	poetry run sphinx-build -b html docs/ docs/_build/html

docs-serve: ## Serve documentation locally
	cd docs/_build/html && python -m http.server 8000

docs-clean: ## Clean documentation build
	rm -rf docs/_build/

# Docker
docker-build: ## Build Docker image
	docker build -t archaeovault:latest .

docker-run: ## Run Docker container
	docker run -p 8080:8080 archaeovault:latest

docker-test: ## Test Docker image
	docker run --rm archaeovault:latest python -c "import app; print('App works!')"

docker-shell: ## Open shell in Docker container
	docker run -it --rm archaeovault:latest /bin/bash

# Development
clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .benchmarks/
	rm -rf bandit-report.json
	rm -rf safety-report.json
	rm -rf pip-audit-report.json
	rm -rf radon-*.json
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build package
	poetry build

# Dependencies
update-deps: ## Update dependencies
	poetry update

update-deps-dev: ## Update development dependencies
	poetry update --with dev

check-deps: ## Check for outdated dependencies
	poetry show --outdated

# Pre-commit
pre-commit: ## Run pre-commit on all files
	poetry run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	poetry run pre-commit autoupdate

# Release
release: ## Create a new release
	poetry run bump2version patch
	git push --tags
	git push

release-minor: ## Create a minor release
	poetry run bump2version minor
	git push --tags
	git push

release-major: ## Create a major release
	poetry run bump2version major
	git push --tags
	git push

# Database
db-migrate: ## Run database migrations
	poetry run alembic upgrade head

db-migrate-create: ## Create a new migration
	poetry run alembic revision --autogenerate -m "$(message)"

db-migrate-downgrade: ## Downgrade database
	poetry run alembic downgrade -1

# Application
run: ## Run the application
	poetry run streamlit run app/app.py

run-dev: ## Run the application in development mode
	poetry run streamlit run app/app.py --server.runOnSave true

# CI/CD
ci-test: ## Run CI tests
	poetry run pytest --cov=app --cov-report=xml --cov-report=html --junitxml=pytest-report.xml

ci-lint: ## Run CI linting
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 .
	poetry run mypy app/ --ignore-missing-imports

ci-security: ## Run CI security checks
	poetry run bandit -r app/ -f json -o bandit-report.json
	poetry run safety check --json --output safety-report.json

# Monitoring
monitor: ## Start application monitoring
	poetry run python -m memory_profiler app/main.py

# Utilities
env-check: ## Check environment variables
	poetry run python -c "from app.config import settings; print('Environment check passed')"

version: ## Show version information
	poetry version
	poetry run python --version
	poetry --version

# Git hooks
git-hooks: ## Install git hooks
	poetry run pre-commit install --hook-type pre-commit
	poetry run pre-commit install --hook-type commit-msg

# Full development setup
setup: install-dev install-pre-commit git-hooks ## Complete development setup
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything works."

# Quick development workflow
dev: format lint test ## Quick development workflow (format, lint, test)

# Production deployment
deploy: clean build docker-build ## Full production deployment pipeline
	@echo "Production deployment complete!"

# Health check
health: ## Check application health
	poetry run python -c "import app; print('Application health check passed')"