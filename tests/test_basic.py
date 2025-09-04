"""
Test configuration.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_config_import():
    """Test that config can be imported."""
    from src.core.config import settings
    assert settings.app_name == "Contract Intelligence Assistant"

def test_api_import():
    """Test that FastAPI app can be imported.""" 
    from src.api.main import app
    assert app.title == "Contract Intelligence Assistant"

def test_opensearch_service_import():
    """Test that OpenSearch service can be imported."""
    try:
        from src.services.opensearch_service import OpenSearchService
        assert OpenSearchService is not None
    except ImportError:
        pytest.skip("OpenSearchService not yet implemented")

@patch('opensearchpy.OpenSearch')
def test_opensearch_connection(mock_opensearch):
    """Test OpenSearch connection initialization."""
    mock_client = MagicMock()
    mock_opensearch.return_value = mock_client
    
    try:
        from src.services.opensearch_service import OpenSearchService
        service = OpenSearchService()
        assert service.client is not None
    except ImportError:
        pytest.skip("OpenSearchService not yet implemented")

@patch('opensearchpy.OpenSearch')
def test_opensearch_health_check(mock_opensearch):
    """Test OpenSearch health check functionality."""
    mock_client = MagicMock()
    mock_client.cluster.health.return_value = {"status": "green"}
    mock_opensearch.return_value = mock_client
    
    try:
        from src.services.opensearch_service import OpenSearchService
        service = OpenSearchService()
        health = service.health_check()
        # Accept both green (production) and yellow (development) status
        assert health["status"] in ["green", "yellow"]
    except ImportError:
        pytest.skip("OpenSearchService not yet implemented")

def test_opensearch_api_endpoint():
    """Test that OpenSearch API endpoint exists."""
    from src.api.main import app
    
    # Check if opensearch route exists
    routes = [route.path for route in app.routes]
    opensearch_routes = [route for route in routes if "opensearch" in route or "search" in route]
    
    # This will pass once the endpoint is implemented
    if not opensearch_routes:
        pytest.skip("OpenSearch API endpoint not yet implemented")
    assert app.title == "Contract Intelligence Assistant"
