"""
Tests for OpenSearch service integration.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestOpenSearchService:
    """Test cases for OpenSearch service."""
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_opensearch_service_initialization(self, mock_opensearch):
        """Test OpenSearch service can be initialized."""
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        assert service.client is not None
        assert service.index_name == "financial_documents"
        
        # Verify client was created with correct config
        mock_opensearch.assert_called_once()
        call_args = mock_opensearch.call_args
        assert call_args[1]['hosts'][0]['host'] == 'localhost'
        assert call_args[1]['hosts'][0]['port'] == 9200
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_health_check_success(self, mock_opensearch):
        """Test successful health check."""
        mock_client = MagicMock()
        mock_client.cluster.health.return_value = {
            "status": "green",
            "cluster_name": "opensearch-cluster",
            "number_of_nodes": 1
        }
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        health = service.health_check()
        
        assert health["status"] == "green"
        assert health["cluster_name"] == "opensearch-cluster"
        mock_client.cluster.health.assert_called_once()
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_health_check_failure(self, mock_opensearch):
        """Test health check when OpenSearch is down."""
        mock_client = MagicMock()
        mock_client.cluster.health.side_effect = Exception("Connection failed")
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        health = service.health_check()
        
        assert health["status"] == "error"
        assert "Connection failed" in health["error"]
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_create_index_success(self, mock_opensearch):
        """Test successful index creation."""
        mock_client = MagicMock()
        mock_client.indices.exists.return_value = False
        mock_client.indices.create.return_value = {"acknowledged": True}
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        result = service.create_index()
        
        assert result is True
        mock_client.indices.exists.assert_called_once_with(index="financial_documents")
        mock_client.indices.create.assert_called_once()
        
        # Verify mapping structure
        create_call_args = mock_client.indices.create.call_args
        mapping = create_call_args[1]['body']
        assert 'mappings' in mapping
        assert 'content' in mapping['mappings']['properties']
        assert 'embedding' in mapping['mappings']['properties']
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_create_index_already_exists(self, mock_opensearch):
        """Test index creation when index already exists."""
        mock_client = MagicMock()
        mock_client.indices.exists.return_value = True
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        result = service.create_index()
        
        assert result is True
        mock_client.indices.exists.assert_called_once()
        mock_client.indices.create.assert_not_called()
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_index_document_success(self, mock_opensearch):
        """Test successful document indexing."""
        mock_client = MagicMock()
        mock_client.index.return_value = {"_id": "doc_123", "result": "created"}
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        document = {
            "content": "Test contract content",
            "title": "Test Contract",
            "partner_name": "Test Partner",
            "document_type": "contract"
        }
        
        result = service.index_document(document, "doc_123")
        
        assert result is True
        mock_client.index.assert_called_once_with(
            index="financial_documents",
            body=document,
            id="doc_123",
            refresh=True
        )
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_search_documents_success(self, mock_opensearch):
        """Test successful document search."""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {
                        "_id": "doc_1",
                        "_score": 1.5,
                        "_source": {"content": "Contract content 1", "partner_name": "Partner A"}
                    },
                    {
                        "_id": "doc_2",
                        "_score": 1.2,
                        "_source": {"content": "Contract content 2", "partner_name": "Partner B"}
                    }
                ]
            }
        }
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        result = service.search_documents("test query", size=5)
        
        assert result["hits"]["total"]["value"] == 2
        assert len(result["hits"]["hits"]) == 2
        assert result["hits"]["hits"][0]["_id"] == "doc_1"
        
        # Verify search query structure
        search_call_args = mock_client.search.call_args
        search_body = search_call_args[1]['body']
        assert search_body['query']['multi_match']['query'] == "test query"
        assert search_body['size'] == 5
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_delete_index_success(self, mock_opensearch):
        """Test successful index deletion."""
        mock_client = MagicMock()
        mock_client.indices.exists.return_value = True
        mock_client.indices.delete.return_value = {"acknowledged": True}
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        result = service.delete_index()
        
        assert result is True
        mock_client.indices.exists.assert_called_once_with(index="financial_documents")
        mock_client.indices.delete.assert_called_once_with(index="financial_documents")
    
    @patch('src.services.opensearch_service.OpenSearch')
    def test_get_document_count(self, mock_opensearch):
        """Test getting document count."""
        mock_client = MagicMock()
        mock_client.count.return_value = {"count": 42}
        mock_opensearch.return_value = mock_client
        
        from src.services.opensearch_service import OpenSearchService
        
        service = OpenSearchService()
        count = service.get_document_count()
        
        assert count == 42
        mock_client.count.assert_called_once_with(index="financial_documents")


class TestOpenSearchAPIEndpoints:
    """Test cases for OpenSearch API endpoints."""
    
    def test_opensearch_router_import(self):
        """Test that OpenSearch router can be imported."""
        from src.api.routers.opensearch import router
        assert router is not None
        assert router.prefix == "/opensearch"
    
    def test_main_app_includes_opensearch_router(self):
        """Test that main app includes OpenSearch router."""
        from src.api.main import app
        
        # Check if opensearch routes are included
        routes = [route.path for route in app.routes]
        opensearch_routes = [route for route in routes if "opensearch" in route]
        
        assert len(opensearch_routes) > 0, "OpenSearch routes should be included in main app"
    
    @patch('src.services.opensearch_service.OpenSearchService')
    def test_health_endpoint_structure(self, mock_service_class):
        """Test health endpoint returns correct structure."""
        from src.api.routers.opensearch import opensearch_health
        
        # Mock the service instance
        mock_service = MagicMock()
        mock_service.health_check.return_value = {"status": "green"}
        mock_service_class.return_value = mock_service
        
        # This would normally be an async test with TestClient, but for now
        # we're just testing the import and basic structure
        assert opensearch_health is not None


# Integration test that can be run with actual OpenSearch
@pytest.mark.integration
class TestOpenSearchIntegration:
    """Integration tests that require actual OpenSearch instance."""
    
    def test_full_opensearch_workflow(self):
        """Test complete OpenSearch workflow with real instance."""
        pytest.skip("Requires running OpenSearch container")
        
        # This test would:
        # 1. Connect to real OpenSearch
        # 2. Create test index
        # 3. Index test document
        # 4. Search for document
        # 5. Verify results
        # 6. Clean up test index


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
