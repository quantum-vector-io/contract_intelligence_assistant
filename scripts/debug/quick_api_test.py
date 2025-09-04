#!/usr/bin/env python3
"""
Quick API test to verify the enhanced analysis is working correctly
"""

import requests
import os

def quick_api_test():
    """Test the API directly to verify enhanced table extraction"""
    print("🧪 Quick API Test - Enhanced Analysis")
    print("=====================================")
    
    # File paths
    contract_path = "data/sample_contracts/4_SkipTheDishesCA_SushiExpress24-7_RestaurantServicesAgreement_2022-03-10.pdf"
    payout_path = "data/sample_contracts/4a_SushiExpress24-7_PayoutReport_2024-07-21.pdf"
    
    try:
        with open(contract_path, 'rb') as contract_file, open(payout_path, 'rb') as payout_file:
            files = {
                'contract_file': (os.path.basename(contract_path), contract_file.read(), 'application/pdf'),
                'payout_file': (os.path.basename(payout_path), payout_file.read(), 'application/pdf')
            }
            
            data = {
                'question': 'How was the $1,902.95 payout calculated? Show the detailed breakdown.',
                'query_database': 'false',
                'action': 'analyze',
                'detailed_report': 'false'
            }
            
            print("🔄 Testing API directly...")
            response = requests.post(
                "http://localhost:8000/analyze",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', 'No answer')
                
                print("✅ API Response received!")
                print()
                print("🔍 Key phrase check:")
                
                if "without the specific payout report" in answer.lower():
                    print("❌ PROBLEM: Still getting 'without payout report' response")
                    print("   This suggests the old code or cached responses")
                else:
                    print("✅ GOOD: Not seeing 'without payout report' message")
                
                if "$1,902.95" in answer or "1902.95" in answer:
                    print("✅ EXCELLENT: Found specific payout amount in response")
                else:
                    print("❌ ISSUE: Specific payout amount not found")
                
                if "delivery commission" in answer.lower() and "714" in answer:
                    print("✅ EXCELLENT: Found delivery commission details")
                else:
                    print("❌ ISSUE: Missing delivery commission details")
                
                print()
                print("📝 Response preview (first 300 chars):")
                print("-" * 50)
                print(answer[:300] + "...")
                print("-" * 50)
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    quick_api_test()
