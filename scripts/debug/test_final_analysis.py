#!/usr/bin/env python3
"""
Final test of the multi-document analysis with enhanced table extraction.
This script tests the complete flow with proper table handling.
"""

import requests
import os
import time

def test_enhanced_analysis():
    """Test the enhanced multi-document analysis with proper table extraction."""
    print("🚀 Testing Enhanced Multi-Document Analysis")
    print("===========================================")
    
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
    
    print(f"📄 Contract file: {os.path.basename(contract_path)}")
    print(f"💰 Payout file: {os.path.basename(payout_path)}")
    
    # Test question that requires both documents
    question = "Analyze the Sushi Express 24/7 contract and payout report. How was the $1,902.95 payout calculated, and do the commission rates match the contract?"
    
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
            
            print("🔄 Uploading files and starting enhanced analysis...")
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
                    print("=" * 70)
                    print(answer)
                    print("=" * 70)
                    print()
                    
                    # Check if the analysis now includes specific details
                    success_indicators = []
                    
                    if any(amount in answer for amount in ['$1,902.95', '1902.95', '$1, 902. 95']):
                        success_indicators.append("✅ Includes specific payout amount")
                    else:
                        success_indicators.append("❌ Missing specific payout amount")
                    
                    if any(term in answer.lower() for term in ['$714', '714.00', 'delivery commission']):
                        success_indicators.append("✅ Includes delivery commission details")
                    else:
                        success_indicators.append("❌ Missing delivery commission details")
                    
                    if any(term in answer.lower() for term in ['28%', '20%', 'commission rate']):
                        success_indicators.append("✅ Includes commission rates")
                    else:
                        success_indicators.append("❌ Missing commission rates")
                    
                    if any(term in answer.lower() for term in ['service fee', '$200', '200.00']):
                        success_indicators.append("✅ Includes service fee details")
                    else:
                        success_indicators.append("❌ Missing service fee details")
                    
                    if any(term in answer.lower() for term in ['total deductions', '$1,022', '1022.05']):
                        success_indicators.append("✅ Includes total deductions")
                    else:
                        success_indicators.append("❌ Missing total deductions")
                    
                    print("📊 Analysis Quality Check:")
                    for indicator in success_indicators:
                        print(f"   {indicator}")
                    
                    success_count = sum(1 for indicator in success_indicators if indicator.startswith("✅"))
                    total_count = len(success_indicators)
                    
                    print()
                    if success_count >= 4:
                        print(f"🎉 SUCCESS! Analysis quality: {success_count}/{total_count} - Excellent detailed analysis!")
                    elif success_count >= 3:
                        print(f"👍 GOOD! Analysis quality: {success_count}/{total_count} - Good analysis with some details!")
                    elif success_count >= 2:
                        print(f"⚠️ PARTIAL! Analysis quality: {success_count}/{total_count} - Basic analysis but missing key details!")
                    else:
                        print(f"❌ POOR! Analysis quality: {success_count}/{total_count} - Analysis lacks important financial details!")
                        
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
    test_enhanced_analysis()
