#!/bin/bash
# ArchaeoVault - Development Environment Setup Script
# Ensures clean coding practices and microservices architecture from day 1

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command_exists docker; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    if ! command_exists git; then
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    log_success "All prerequisites are installed."
}

# Create environment file
setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f env.template ]; then
            cp env.template .env
            log_success "Created .env file from template."
            log_warning "Please update .env file with your actual API keys and configuration."
        else
            log_error "env.template file not found. Please create it first."
            exit 1
        fi
    else
        log_info ".env file already exists. Skipping creation."
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p reports
    mkdir -p temp
    mkdir -p backups
    mkdir -p test_reports
    mkdir -p performance_reports
    mkdir -p security_reports
    mkdir -p quality_reports
    mkdir -p seed_data
    
    log_success "Created all necessary directories."
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
        log_success "Installed production dependencies."
    else
        log_error "requirements.txt not found."
        exit 1
    fi
    
    if [ -f requirements-dev.txt ]; then
        pip install -r requirements-dev.txt
        log_success "Installed development dependencies."
    else
        log_warning "requirements-dev.txt not found. Skipping development dependencies."
    fi
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."
    
    if command_exists pre-commit; then
        pre-commit install
        log_success "Pre-commit hooks installed."
    else
        log_warning "pre-commit not found. Skipping pre-commit setup."
    fi
}

# Build Docker images
build_docker_images() {
    log_info "Building Docker images..."
    
    docker-compose build
    log_success "Docker images built successfully."
}

# Start services
start_services() {
    log_info "Starting services..."
    
    # Start database and cache first
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # Start application
    docker-compose up -d app
    
    log_success "Services started successfully."
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    docker-compose run --rm migrate
    log_success "Database migrations completed."
}

# Seed database
seed_database() {
    log_info "Seeding database with sample data..."
    
    docker-compose run --rm seed
    log_success "Database seeded successfully."
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    docker-compose run --rm test
    log_success "Tests completed successfully."
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring services..."
    
    docker-compose --profile monitoring up -d
    log_success "Monitoring services started."
    log_info "Grafana: http://localhost:3000 (admin/admin123)"
    log_info "Prometheus: http://localhost:9090"
}

# Setup logging
setup_logging() {
    log_info "Setting up logging services..."
    
    docker-compose --profile logging up -d
    log_success "Logging services started."
    log_info "Kibana: http://localhost:5601"
    log_info "Elasticsearch: http://localhost:9200"
}

# Show status
show_status() {
    log_info "Service Status:"
    echo "==============="
    docker-compose ps
    
    echo ""
    log_info "Application URLs:"
    echo "=================="
    echo "Main App: http://localhost:8501"
    echo "Database Admin: http://localhost:5050"
    echo "Redis Admin: http://localhost:8081"
    echo "API Docs: http://localhost:8080"
    echo "Jupyter: http://localhost:8888"
    
    if docker-compose ps | grep -q "prometheus"; then
        echo "Prometheus: http://localhost:9090"
        echo "Grafana: http://localhost:3000"
    fi
    
    if docker-compose ps | grep -q "kibana"; then
        echo "Kibana: http://localhost:5601"
    fi
}

# Main setup function
main() {
    log_info "Starting ArchaeoVault development environment setup..."
    echo "========================================================"
    
    check_prerequisites
    setup_environment
    create_directories
    install_dependencies
    setup_pre_commit
    build_docker_images
    start_services
    run_migrations
    seed_database
    run_tests
    
    echo ""
    log_success "Development environment setup completed successfully!"
    echo ""
    show_status
    
    echo ""
    log_info "Next steps:"
    echo "==========="
    echo "1. Update .env file with your API keys"
    echo "2. Access the application at http://localhost:8501"
    echo "3. Run 'make dev' to start development mode"
    echo "4. Run 'make test' to run tests"
    echo "5. Run 'make lint' to check code quality"
    echo "6. Run 'make format' to format code"
    echo ""
    log_info "For more commands, run 'make help'"
}

# Run main function
main "$@"

