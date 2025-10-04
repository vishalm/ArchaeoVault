# ArchaeoVault Makefile
# Provides convenient commands for development and deployment

.PHONY: help install run test clean lint format

# Default target
help:
	@echo "🏺 ArchaeoVault - Available Commands:"
	@echo ""
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run the application"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean up generated files"
	@echo "  make help       - Show this help message"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

# Run the application
run:
	@echo "🚀 Starting ArchaeoVault..."
	python run.py

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest

# Run linting
lint:
	@echo "🔍 Running linting..."
	flake8 app/
	mypy app/
	pylint app/

# Format code
format:
	@echo "🎨 Formatting code..."
	black app/
	isort app/

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Development setup
dev-setup: install
	@echo "🔧 Setting up development environment..."
	pre-commit install
	@echo "✅ Development environment ready!"

# Quick start (install and run)
quick-start: install run