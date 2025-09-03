"""
Integration tests for the complete system workflow.
Tests end-to-end functionality from document upload to AI analysis.
"""
import pytest
import requests
import time
from pathlib import Path


class TestSystemIntegration:
    """Test complete system integration."""
    
    def test_health_endpoints(self, api_base_url, opensearch_url):
        """Test that all system components are healthy."""
        # Test API health
        api_response = requests.get(f"{api_base_url}/health", timeout=10)
        assert api_response.status_code == 200
        
        # Test OpenSearch health
        opensearch_response = requests.get(f"{opensearch_url}/_cluster/health", timeout=10)
        assert opensearch_response.status_code == 200
    
    def test_document_analysis_workflow(self, api_base_url, test_data_dir):
        """Test complete document analysis workflow."""
        # Prepare test files
        contract_file = test_data_dir / "Sushi_Express_Contract.txt"
        payout_file = test_data_dir / "Sushi_Express_Payout_Report.txt"
        
        assert contract_file.exists(), f"Contract file not found: {contract_file}"
        assert payout_file.exists(), f"Payout file not found: {payout_file}"
        
        # Test analysis endpoint
        with open(contract_file, 'rb') as cf, open(payout_file, 'rb') as pf:
            files = {
                'contract_file': ('contract.txt', cf, 'text/plain'),
                'payout_file': ('payout.txt', pf, 'text/plain')
            }
            data = {
                'question': 'What is the commission rate in this contract?'
            }
            
            response = requests.post(
                f"{api_base_url}/analyze",
                files=files,
                data=data,
                timeout=60
            )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["analysis_successful"] == True
        assert len(result["answer"]) > 0
    
    def test_database_query_functionality(self, api_base_url):
        """Test database querying functionality."""
        query_data = {
            'question': 'What commission rates are available in the database?'
        }
        
        response = requests.post(
            f"{api_base_url}/query",
            json=query_data,
            timeout=30
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert len(result["answer"]) > 0

    def test_opensearch_index_status(self, opensearch_url):
        """Test OpenSearch index status and document count."""
        response = requests.get(
            f"{opensearch_url}/financial_documents/_count",
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["count"] > 0, "No documents found in OpenSearch index"
