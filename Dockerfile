# Multi-stage Dockerfile for ArchaeoVault
# Supports development, testing, and production environments

# Base stage with common dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r archaeo && useradd -r -g archaeo archaeo

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/reports /app/temp /app/logs && \
    chown -R archaeo:archaeo /app

# Switch to non-root user
USER archaeo

# Expose port
EXPOSE 8501

# Default command for development
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Testing stage
FROM development as testing

# Install additional testing dependencies
RUN pip install pytest-cov pytest-xdist pytest-asyncio pytest-mock \
    locust bandit safety semgrep black isort flake8 mypy pylint

# Copy test configuration
COPY pytest.ini .pytest_cache/ ./

# Set testing environment
ENV APP_ENV=testing \
    PYTEST_CURRENT_TEST=true

# Default command for testing
CMD ["pytest", "tests/", "-v", "--cov=app", "--cov-report=html", "--cov-report=xml"]

# Production stage
FROM base as production

# Install production dependencies only
RUN pip install --no-deps -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/reports /app/temp /app/logs && \
    chown -R archaeo:archaeo /app

# Switch to non-root user
USER archaeo

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# Default command for production
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]

# CI/CD stage for GitHub Actions
FROM testing as ci

# Install CI-specific dependencies
RUN pip install coverage[toml] codecov

# Set CI environment
ENV CI=true \
    COVERAGE_FILE=/app/.coverage

# Default command for CI
CMD ["pytest", "tests/", "-v", "--cov=app", "--cov-report=xml", "--cov-report=term", "--junitxml=test-results.xml"]

