"""
Demo script to test OpenSearch API endpoints.
This script demonstrates how to use the OpenSearch service through the API.
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_opensearch_api():
    """Test OpenSearch API endpoints."""
    print("🔍 Testing OpenSearch API Integration")
    print("=" * 50)
    
    # Test basic health check
    print("\n1. Testing basic API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Basic API health check: PASSED")
        else:
            print(f"❌ Basic API health check: FAILED ({response.status_code})")
    except requests.ConnectionError:
        print("❌ API is not running. Start it with: uvicorn src.api.main:app --reload")
        return False
    
    # Test OpenSearch health
    print("\n2. Testing OpenSearch health...")
    try:
        response = requests.get(f"{BASE_URL}/opensearch/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OpenSearch health check: {data['status']}")
            if data['status'] == 'success':
                print(f"   Cluster status: {data['data'].get('status', 'unknown')}")
            else:
                print(f"   Note: This will show 'error' if OpenSearch container is not running")
        else:
            print(f"❌ OpenSearch health check: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ OpenSearch health check: ERROR - {e}")
    
    # Test index creation
    print("\n3. Testing index creation...")
    try:
        response = requests.post(f"{BASE_URL}/opensearch/index/create")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Index creation: {data['status']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"⚠️  Index creation: Status {response.status_code}")
            print(f"   Note: This will fail if OpenSearch container is not running")
    except Exception as e:
        print(f"❌ Index creation: ERROR - {e}")
    
    # Test search (will return empty results)
    print("\n4. Testing search functionality...")
    try:
        response = requests.get(f"{BASE_URL}/opensearch/search?q=test&size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search functionality: {data['status']}")
            print(f"   Results found: {data['data']['total']}")
        else:
            print(f"⚠️  Search functionality: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Search functionality: ERROR - {e}")
    
    # Test index stats
    print("\n5. Testing index statistics...")
    try:
        response = requests.get(f"{BASE_URL}/opensearch/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Index statistics: {data['status']}")
            if data['status'] == 'success':
                stats = data['data']
                print(f"   Index: {stats['index_name']}")
                print(f"   Documents: {stats['document_count']}")
                print(f"   Cluster: {stats['cluster_status']}")
        else:
            print(f"⚠️  Index statistics: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Index statistics: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Testing Complete!")
    print("\nNext Steps:")
    print("1. Start OpenSearch with: docker-compose up opensearch")
    print("2. Start API with: uvicorn src.api.main:app --reload")
    print("3. View API docs at: http://localhost:8000/docs")
    print("4. Test endpoints with this script: python scripts/test_opensearch_api.py")
    
    return True

if __name__ == "__main__":
    test_opensearch_api()
