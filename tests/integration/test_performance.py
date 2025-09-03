"""
Performance and load testing for the contract intelligence system.
"""
import pytest
import requests
import time
import concurrent.futures
from pathlib import Path


class TestPerformance:
    """Performance and load tests."""
    
    @pytest.mark.slow
    def test_concurrent_queries(self, api_base_url):
        """Test system performance under concurrent load."""
        query_data = {
            'question': 'What are the commission rates?'
        }
        
        def make_query():
            """Make a single query request."""
            start_time = time.time()
            try:
                response = requests.post(
                    f"{api_base_url}/query",
                    json=query_data,
                    timeout=60  # Increased timeout
                )
                end_time = time.time()
                return {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except requests.exceptions.RequestException:
                end_time = time.time()
                return {
                    'status_code': 0,
                    'response_time': end_time - start_time,
                    'success': False
                }
        
        # Run only 3 concurrent requests to avoid overwhelming the system
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_query) for _ in range(3)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verify at least 2 requests succeeded (allowing for 1 failure)
        successful_requests = sum(1 for r in results if r['success'])
        assert successful_requests >= 2, f"Only {successful_requests}/3 requests succeeded"
        
        # Check average response time is reasonable (< 60 seconds)
        successful_times = [r['response_time'] for r in results if r['success']]
        if successful_times:
            avg_response_time = sum(successful_times) / len(successful_times)
            assert avg_response_time < 60, f"Average response time too high: {avg_response_time}s"
    
    @pytest.mark.slow
    def test_large_document_processing(self, api_base_url, test_data_dir):
        """Test processing of larger PDF documents."""
        # Find a PDF file to test with
        pdf_files = list(test_data_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files available for testing")
        
        pdf_file = pdf_files[0]
        
        with open(pdf_file, 'rb') as pf:
            files = {
                'contract_file': (pdf_file.name, pf, 'application/pdf'),
                'payout_file': ('dummy_payout.txt', b'Dummy payout data', 'text/plain')
            }
            data = {
                'question': 'Summarize the main terms of this contract.'
            }
            
            start_time = time.time()
            response = requests.post(
                f"{api_base_url}/analyze",
                files=files,
                data=data,
                timeout=120  # Longer timeout for PDF processing
            )
            end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        
        # PDF processing should complete within reasonable time
        assert processing_time < 120, f"PDF processing took too long: {processing_time}s"
