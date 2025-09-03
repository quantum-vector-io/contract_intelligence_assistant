"""Test configuration and common utilities."""
import pytest
import sys
import os
from pathlib import Path

# Add src to Python path for all tests
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing path to test data directory."""
    return ROOT_DIR / "data" / "sample_contracts"

@pytest.fixture(scope="session") 
def api_base_url():
    """Fixture providing API base URL for integration tests."""
    return "http://localhost:8000"

@pytest.fixture(scope="session")
def opensearch_url():
    """Fixture providing OpenSearch URL for integration tests."""
    return "http://localhost:9200"

# Test markers
pytest_mark_unit = pytest.mark.unit
pytest_mark_integration = pytest.mark.integration
pytest_mark_slow = pytest.mark.slow
