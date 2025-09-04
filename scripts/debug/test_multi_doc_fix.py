#!/usr/bin/env python3
"""
Test script to verify the multi-document analysis fix.
This script uploads both Sushi Express files and tests the analysis.
"""

import requests
import os
import time

def test_multi_document_analysis():
    """Test uploading both contract and payout files and analyzing them together."""
    print("🔄 Testing Multi-Document Analysis Fix")
    print("=====================================")
    
    # File paths
    contract_path = "data/sample_contracts/4_SkipTheDishesCA_SushiExpress24-7_RestaurantServicesAgreement_2022-03-10.pdf"
    payout_path = "data/sample_contracts/4a_SushiExpress24-7_PayoutReport_2024-07-21.pdf"
    
    # Check files exist
    if not os.path.exists(contract_path):
        print(f"❌ Contract file not found: {contract_path}")
        return
    if not os.path.exists(payout_path):
        print(f"❌ Payout file not found: {payout_path}")
        return
    
    print(f"📄 Contract file: {contract_path}")
    print(f"💰 Payout file: {payout_path}")
    
    # Test question
    question = "Analyze the 'Sushi Express 24/7' contract and their latest payout report. How was the $1,902.95 payout calculated?"
    
    print(f"❓ Question: {question}")
    print()
    
    try:
        # Prepare files for upload
        with open(contract_path, 'rb') as contract_file, open(payout_path, 'rb') as payout_file:
            files = {
                'contract_file': (os.path.basename(contract_path), contract_file.read(), 'application/pdf'),
                'payout_file': (os.path.basename(payout_path), payout_file.read(), 'application/pdf')
            }
            
            data = {
                'question': question,
                'query_database': 'false',  # Use uploaded files only
                'action': 'analyze',
                'detailed_report': 'false'
            }
            
            print("🚀 Uploading files and starting analysis...")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/analyze",
                files=files,
                data=data,
                timeout=120
            )
            
            end_time = time.time()
            print(f"⏱️ Analysis completed in {end_time - start_time:.2f} seconds")
            print()
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Analysis Successful!")
                print(f"📊 Status: {result.get('status')}")
                print(f"📄 Contract indexed: {result.get('contract_indexed')}")
                print(f"💰 Payout indexed: {result.get('payout_indexed')}")
                print(f"🎯 Analysis successful: {result.get('analysis_successful')}")
                print()
                
                if result.get('analysis_successful'):
                    answer = result.get('answer', 'No answer provided')
                    print("🤖 AI Analysis:")
                    print("=" * 50)
                    print(answer)
                    print("=" * 50)
                    
                    # Check if the answer mentions payout information
                    if any(keyword in answer.lower() for keyword in ['$1,902.95', '1902.95', 'payout report', 'total earnings', 'deduction']):
                        print("✅ SUCCESS: Analysis includes payout report information!")
                    else:
                        print("❌ ISSUE: Analysis doesn't seem to include payout report details")
                        
                else:
                    print(f"❌ Analysis failed: {result.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Error details: {error_detail}")
                except:
                    print(f"Response text: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_multi_document_analysis()
