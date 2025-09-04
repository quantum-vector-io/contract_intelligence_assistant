"""
Test script for the financial analysis API endpoints.
"""
import requests
import json

# Test the financial analysis API
base_url = "http://localhost:8000"

def test_financial_analysis_api():
    """Test the financial analysis endpoints."""
    print("🧪 Testing Financial Analysis API")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Test financial analysis endpoint
    try:
        # Test simple query
        query_data = {
            "question": "What are the commission rates in the contracts?",
            "partner_id": "sushi_express"
        }
        
        response = requests.post(
            f"{base_url}/financial-analysis/analyze",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Analysis endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful!")
            print(f"🔍 Answer: {result.get('answer', 'No answer')[:200]}...")
            print(f"📄 Sources: {len(result.get('sources', []))} documents")
        else:
            print(f"❌ Analysis failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
    
    # Test discrepancy analysis
    try:
        discrepancy_data = {
            "question": "Explain the discrepancies in this payout report based on the provided contract.",
            "partner_id": "sushi_express"
        }
        
        response = requests.post(
            f"{base_url}/financial-analysis/analyze-discrepancies",
            json=discrepancy_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Discrepancy analysis status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Discrepancy analysis successful!")
            print(f"🔍 Answer: {result.get('answer', 'No answer')[:300]}...")
            print(f"📄 Sources: {len(result.get('sources', []))} documents")
        else:
            print(f"❌ Discrepancy analysis failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Discrepancy analysis test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Financial Analysis API Test Complete!")

if __name__ == "__main__":
    test_financial_analysis_api()
