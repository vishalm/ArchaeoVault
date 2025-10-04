# ArchaeoVault Test Suite
"""
Comprehensive test suite for ArchaeoVault agentic AI archaeological platform.

This package contains all tests for the application, organized by:
- Unit tests for individual components
- Integration tests for service interactions
- End-to-end tests for complete workflows
- Performance tests for scalability
- Security tests for vulnerability assessment

Test Structure:
- tests/unit/ - Unit tests for individual components
- tests/integration/ - Integration tests for service interactions
- tests/e2e/ - End-to-end tests for complete workflows
- tests/performance/ - Performance and load tests
- tests/security/ - Security and vulnerability tests
- tests/fixtures/ - Test fixtures and factories
- tests/utils/ - Test utilities and helpers
"""

import pytest
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Test configuration
@dataclass
class TestConfig:
    """Test configuration settings"""
    ai_api_key: str = "test-key"
    database_url: str = "sqlite:///test.db"
    redis_url: str = "redis://localhost:6379/1"
    debug_mode: bool = True
    test_timeout: int = 30

# Global test fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_config():
    """Provide test configuration"""
    return TestConfig()

# Test markers
pytest_plugins = ["pytest_asyncio"]

# Test categories
pytestmark = [
    pytest.mark.asyncio,
]
