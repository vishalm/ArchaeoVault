"""
Pytest configuration and shared fixtures for ArchaeoVault tests.

This module provides:
- Shared test fixtures
- Test configuration
- Mock services
- Test data factories
- Database setup/teardown
- AI service mocking
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Generator
import json

# Test imports
from app.config import Settings, AISettings, DatabaseSettings, RedisSettings, LoggingSettings
from app.models.artifact import Artifact, ArtifactData
from app.models.civilization import Civilization, CivilizationData
from app.models.excavation import Excavation, ExcavationData
from app.services.ai_orchestrator import AIOrchestrator
from app.services.ai_agents.base_agent import AgentConfig

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_config():
    """Provide test configuration"""
    return Settings(
        app_env="testing",
        debug_mode=True,
        ai=AISettings(anthropic_api_key="test-key"),
        database=DatabaseSettings(url="sqlite:///test.db"),
        redis=RedisSettings(url="redis://localhost:6379/1"),
        logging=LoggingSettings(level="DEBUG")
    )

@pytest.fixture
def test_agent_config():
    """Provide test agent configuration"""
    return AgentConfig(
        api_key="test-key",
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        max_tokens=4000,
        timeout=30,
        agent_name="TestAgent",
        max_retries=3,
        retry_delay=1.0,
        cache_ttl=3600,
        memory_enabled=True,
        memory_size=1000,
        memory_ttl=86400,
        tools_enabled=True,
        max_tool_calls=10,
        tool_timeout=15
    )

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

# Database fixtures
@pytest.fixture
async def test_db():
    """Create test database"""
    # Setup test database
    yield "test_db_connection"
    # Teardown test database

# Mock AI services
@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client"""
    with patch('anthropic.Anthropic') as mock_client:
        mock_instance = Mock()
        mock_instance.messages.create = AsyncMock(return_value=Mock(
            content=[Mock(text="Test AI response")]
        ))
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_ai_analyzer(mock_anthropic_client):
    """Mock AI analyzer service"""
    with patch('app.services.ai_agents.artifact_agent.ArtifactAnalysisAgent') as mock_analyzer:
        mock_instance = Mock()
        mock_instance.process = AsyncMock(return_value=Mock(
            success=True,
            data={
                "description": "Test artifact analysis",
                "confidence": 0.85,
                "civilization": "Test Civilization",
                "dating_estimate": "1000-800 BCE"
            }
        ))
        mock_analyzer.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_agent_orchestrator():
    """Mock AI agent orchestrator"""
    with patch('app.services.ai_orchestrator.AIOrchestrator') as mock_orchestrator:
        mock_instance = Mock()
        mock_instance.process_complex_request = AsyncMock(return_value={
            "artifact_analysis": {"confidence": 0.85},
            "civilization_context": {"name": "Test Civ"},
            "dating_analysis": {"age": "1000 BCE"}
        })
        mock_orchestrator.return_value = mock_instance
        yield mock_instance

# Test data factories
@pytest.fixture
def sample_artifact_data():
    """Sample artifact data for testing"""
    return ArtifactData(
        name="Test Pottery Vase",
        material="ceramic",
        period="Bronze Age",
        condition_score=8,
        location={"lat": 40.7128, "lon": -74.0060, "site_name": "Test Site"},
        discovery_date="2024-01-01",
        image_urls=["test_image.jpg"],
        metadata={"color": "red", "decoration": "geometric"}
    )

@pytest.fixture
def sample_civilization_data():
    """Sample civilization data for testing"""
    return CivilizationData(
        name="Test Civilization",
        time_period=(3000, 1000),
        region="Test Region",
        achievements=["Writing", "Architecture", "Art"],
        notable_artifacts=["Test Artifact 1", "Test Artifact 2"],
        cultural_data={"language": "Test Language", "religion": "Test Religion"}
    )

@pytest.fixture
def sample_excavation_data():
    """Sample excavation data for testing"""
    return ExcavationData(
        site_name="Test Excavation Site",
        location={"lat": 40.7128, "lon": -74.0060},
        grid_size={"width": 10, "height": 10},
        layers=[
            {"depth": 0.5, "soil_type": "topsoil", "artifacts": []},
            {"depth": 1.0, "soil_type": "clay", "artifacts": ["pottery"]}
        ],
        findings=["Test Finding 1", "Test Finding 2"],
        status="planned"
    )

# Mock external services
@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    with patch('redis.Redis') as mock_redis:
        mock_instance = Mock()
        mock_instance.get = AsyncMock(return_value=None)
        mock_instance.set = AsyncMock(return_value=True)
        mock_instance.setex = AsyncMock(return_value=True)
        mock_instance.delete = AsyncMock(return_value=1)
        mock_redis.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_database():
    """Mock database connection"""
    with patch('app.services.database.DatabaseManager') as mock_db:
        mock_connection = Mock()
        mock_connection.execute = AsyncMock()
        mock_connection.fetch = AsyncMock(return_value=[])
        mock_connection.fetchrow = AsyncMock(return_value=None)
        mock_db.return_value = mock_connection
        yield mock_connection

# Test utilities
@pytest.fixture
def test_image_file(temp_dir):
    """Create test image file"""
    image_path = os.path.join(temp_dir, "test_image.jpg")
    # Create a simple test image file
    with open(image_path, "wb") as f:
        f.write(b"fake_image_data")
    return image_path

@pytest.fixture
def test_json_file(temp_dir):
    """Create test JSON file"""
    json_path = os.path.join(temp_dir, "test_data.json")
    test_data = {
        "artifacts": [
            {"name": "Test Artifact 1", "material": "ceramic"},
            {"name": "Test Artifact 2", "material": "metal"}
        ],
        "civilizations": [
            {"name": "Test Civ 1", "period": "Bronze Age"},
            {"name": "Test Civ 2", "period": "Iron Age"}
        ]
    }
    with open(json_path, "w") as f:
        json.dump(test_data, f)
    return json_path

# Performance test fixtures
@pytest.fixture
def performance_test_data():
    """Generate large dataset for performance testing"""
    return {
        "artifacts": [
            {
                "id": f"artifact_{i}",
                "name": f"Test Artifact {i}",
                "material": "ceramic" if i % 2 == 0 else "metal",
                "period": "Bronze Age" if i % 3 == 0 else "Iron Age"
            }
            for i in range(1000)
        ],
        "civilizations": [
            {
                "id": f"civ_{i}",
                "name": f"Test Civilization {i}",
                "period": (3000 - i * 100, 2000 - i * 100)
            }
            for i in range(100)
        ]
    }

# Security test fixtures
@pytest.fixture
def malicious_inputs():
    """Malicious inputs for security testing"""
    return {
        "sql_injection": [
            "'; DROP TABLE artifacts; --",
            "1' OR '1'='1",
            "admin'--"
        ],
        "xss_payloads": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd"
        ]
    }

# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "ai_agents: AI agent tests")
    config.addinivalue_line("markers", "slow: Slow running tests")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        elif "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        elif "security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        elif "agent" in item.nodeid:
            item.add_marker(pytest.mark.ai_agents)

