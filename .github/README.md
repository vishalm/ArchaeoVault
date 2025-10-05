# GitHub Actions CI/CD Pipeline

This repository uses a comprehensive GitHub Actions CI/CD pipeline with world-class standards for code quality, testing, security, and deployment.

## 🚀 Pipeline Overview

Our CI/CD pipeline consists of multiple workflows that ensure code quality, security, and reliability:

### 1. **CI Pipeline** (`.github/workflows/ci.yml`)
- **Code Quality & Linting**: Black, isort, flake8, mypy, bandit
- **Unit Tests**: pytest with coverage reporting
- **Integration Tests**: Database and service integration tests
- **Security Scanning**: Safety, pip-audit, Semgrep
- **Docker Build & Test**: Multi-architecture builds
- **Performance Testing**: Benchmark and profiling
- **Quality Gate**: Ensures all checks pass before deployment

### 2. **Dependency Management** (`.github/workflows/dependencies.yml`)
- **Weekly Updates**: Automated dependency updates
- **Security Audits**: Vulnerability scanning
- **License Checks**: Open source license compliance
- **Automated PRs**: Creates PRs for dependency updates

### 3. **Code Quality** (`.github/workflows/quality.yml`)
- **SonarCloud Integration**: Code quality analysis
- **CodeQL Analysis**: GitHub's security analysis
- **Complexity Monitoring**: Radon, Xenon analysis
- **Dead Code Detection**: Vulture analysis
- **Documentation Quality**: Sphinx builds and link checking

### 4. **Docker Registry** (`.github/workflows/docker.yml`)
- **Multi-Architecture Builds**: AMD64 and ARM64 support
- **Security Scanning**: Trivy vulnerability scanning
- **Image Size Monitoring**: Prevents bloated images
- **Registry Cleanup**: Automated cleanup of old images

### 5. **Release Management** (`.github/workflows/release.yml`)
- **Automated Releases**: Tag-based releases
- **Changelog Generation**: Automatic changelog creation
- **PyPI Publishing**: Automated package publishing
- **Documentation Deployment**: GitHub Pages deployment
- **Notifications**: Slack/Discord notifications

## 📊 Quality Gates

Our pipeline enforces strict quality gates:

- **Test Coverage**: Minimum 80% coverage required
- **Code Quality**: All linting checks must pass
- **Security**: No high/critical vulnerabilities allowed
- **Performance**: No significant performance regressions
- **Documentation**: Docstring coverage requirements

## 🛠️ Development Workflow

### Local Development
```bash
# Install dependencies
make install-dev

# Install pre-commit hooks
make install-pre-commit

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Run security checks
make security-check
```

### Pre-commit Hooks
We use pre-commit hooks to ensure code quality before commits:
- Code formatting (Black, isort)
- Linting (flake8, mypy)
- Security checks (bandit, safety)
- Type checking (mypy)
- Documentation checks (interrogate)

### Branch Protection
- **main**: Requires PR reviews, all checks must pass
- **develop**: Requires PR reviews, all checks must pass
- **feature/**: No restrictions, but CI runs on PRs

## 🔒 Security Features

### Vulnerability Scanning
- **Dependencies**: Safety and pip-audit
- **Code**: Bandit and Semgrep
- **Containers**: Trivy scanning
- **Secrets**: Detect-secrets

### Security Policies
- No hardcoded secrets
- Regular dependency updates
- Automated security scanning
- Vulnerability disclosure process

## 📈 Monitoring & Metrics

### Code Quality Metrics
- Test coverage percentage
- Code complexity scores
- Maintainability index
- Technical debt ratio

### Performance Metrics
- Test execution time
- Build time
- Docker image size
- Memory usage

### Security Metrics
- Vulnerability count by severity
- Dependency update frequency
- Security scan results
- License compliance

## 🚀 Deployment

### Environments
- **Staging**: Auto-deploy from `develop` branch
- **Production**: Auto-deploy from `main` branch
- **Feature**: Manual deployment for testing

### Deployment Strategy
- Blue-green deployments
- Automated rollback on failure
- Health checks after deployment
- Database migration handling

## 📚 Documentation

### Generated Documentation
- API documentation (Sphinx)
- Code coverage reports
- Performance benchmarks
- Security scan reports

### Documentation Sites
- **Main Docs**: [archaeovault.dev](https://archaeovault.dev)
- **API Docs**: [api.archaeovault.dev](https://api.archaeovault.dev)
- **Coverage**: [coverage.archaeovault.dev](https://coverage.archaeovault.dev)

## 🔧 Configuration

### Environment Variables
Required secrets in GitHub repository settings:
- `PYPI_API_TOKEN`: For PyPI publishing
- `SONAR_TOKEN`: For SonarCloud analysis
- `SLACK_WEBHOOK_URL`: For notifications
- `DISCORD_WEBHOOK_URL`: For notifications

### Workflow Configuration
- Python versions: 3.10, 3.11
- Node.js version: 18
- Poetry version: 1.6.1
- Docker platforms: linux/amd64, linux/arm64

## 📋 Troubleshooting

### Common Issues
1. **Test Failures**: Check test logs and fix failing tests
2. **Linting Errors**: Run `make format` and `make lint`
3. **Security Issues**: Review security scan reports
4. **Build Failures**: Check Docker build logs
5. **Deployment Issues**: Check deployment logs and health checks

### Getting Help
- Check workflow logs in GitHub Actions
- Review error messages and stack traces
- Consult team documentation
- Create an issue for persistent problems

## 🎯 Best Practices

### Code Quality
- Write comprehensive tests
- Follow coding standards
- Document your code
- Keep functions small and focused
- Use type hints

### Security
- Never commit secrets
- Keep dependencies updated
- Follow security guidelines
- Report vulnerabilities responsibly

### Performance
- Profile your code
- Optimize database queries
- Use async operations
- Monitor resource usage

### Documentation
- Keep README updated
- Document API changes
- Write clear commit messages
- Update changelog

## 📞 Support

For questions about the CI/CD pipeline:
- Create an issue in this repository
- Contact the DevOps team
- Check the documentation
- Review workflow logs

---

**Last Updated**: $(date)
**Pipeline Version**: 1.0.0
**Maintainer**: DevOps Team
