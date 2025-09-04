#!/usr/bin/env python3
"""
Test the enhanced multi-document analysis with Docker environment.
This script tests the complete flow with proper table handling in Docker.
"""

import requests
import os
import time
import json

def test_docker_services():
    """Test that Docker services are accessible."""
    print("🐳 Testing Docker Services")
    print("==========================")
    
    # Test API health
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ API service is accessible")
        else:
            print(f"❌ API service returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API service not accessible: {str(e)}")
        return False
    
    # Test OpenSearch
    try:
        response = requests.get("http://localhost:9200/_cluster/health", timeout=10)
        if response.status_code == 200:
            print("✅ OpenSearch is accessible")
        else:
            print(f"❌ OpenSearch returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenSearch not accessible: {str(e)}")
        return False
    
    print()
    return True

def test_enhanced_docker_analysis():
    """Test the enhanced multi-document analysis in Docker environment."""
    print("🚀 Testing Enhanced Multi-Document Analysis in Docker")
    print("=====================================================")
    
    # First test Docker services
    if not test_docker_services():
        print("❌ Docker services not ready. Aborting test.")
        return
    
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
    
    # Comprehensive test question
    question = "Analyze the Sushi Express 24/7 contract and payout report. How was the $1,902.95 payout calculated? Show the breakdown of commissions, fees, and deductions. Do the commission rates in the payout match what's specified in the contract?"
    
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
            
            print("🔄 Uploading files and starting Docker-based analysis...")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/analyze",
                files=files,
                data=data,
                timeout=180  # Longer timeout for Docker
            )
            
            end_time = time.time()
            print(f"⏱️ Analysis completed in {end_time - start_time:.2f} seconds")
            print()
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Docker Analysis Successful!")
                print(f"📊 Status: {result.get('status')}")
                print(f"📄 Contract indexed: {result.get('contract_indexed')}")
                print(f"💰 Payout indexed: {result.get('payout_indexed')}")
                print(f"🎯 Analysis successful: {result.get('analysis_successful')}")
                print()
                
                if result.get('analysis_successful'):
                    answer = result.get('answer', 'No answer provided')
                    print("🤖 AI Analysis from Docker:")
                    print("=" * 80)
                    print(answer)
                    print("=" * 80)
                    print()
                    
                    # Comprehensive analysis quality check
                    quality_checks = [
                        {
                            'name': 'Specific Payout Amount',
                            'keywords': ['$1,902.95', '1902.95', '$1, 902. 95', '1,902.95'],
                            'weight': 2
                        },
                        {
                            'name': 'Delivery Commission',
                            'keywords': ['$714', '714.00', '$714.00', 'delivery commission'],
                            'weight': 2
                        },
                        {
                            'name': 'Commission Rates',
                            'keywords': ['28%', '20%', 'commission rate', 'twenty percent', 'twenty-eight'],
                            'weight': 2
                        },
                        {
                            'name': 'Service Fees',
                            'keywords': ['service fee', '$200', '200.00', '$2.00', 'per order'],
                            'weight': 1
                        },
                        {
                            'name': 'Total Deductions',
                            'keywords': ['total deductions', '$1,022', '1022.05', '$1, 022. 05'],
                            'weight': 1
                        },
                        {
                            'name': 'Gross Sales',
                            'keywords': ['gross sales', '$2,925', '2925.00', '$2, 925. 00'],
                            'weight': 1
                        },
                        {
                            'name': 'Pickup Commission',
                            'keywords': ['pickup commission', '$75', '75.00', '$375'],
                            'weight': 1
                        },
                        {
                            'name': 'Customer Refunds',
                            'keywords': ['customer refund', '$25.50', 'order #10234', 'wrong item'],
                            'weight': 1
                        },
                        {
                            'name': 'Penalties',
                            'keywords': ['penalty', 'courier wait time', '$5.00', 'order error'],
                            'weight': 1
                        },
                        {
                            'name': 'Contract Verification',
                            'keywords': ['contract', 'agreement', 'terms', 'match', 'consistent'],
                            'weight': 1
                        }
                    ]
                    
                    total_score = 0
                    max_score = 0
                    results = []
                    
                    for check in quality_checks:
                        found = any(keyword.lower() in answer.lower() for keyword in check['keywords'])
                        score = check['weight'] if found else 0
                        total_score += score
                        max_score += check['weight']
                        
                        status = "✅" if found else "❌"
                        results.append(f"   {status} {check['name']} (Weight: {check['weight']})")
                    
                    print("📊 Detailed Analysis Quality Check:")
                    for result in results:
                        print(result)
                    
                    percentage = (total_score / max_score) * 100
                    print()
                    print(f"🎯 Overall Score: {total_score}/{max_score} ({percentage:.1f}%)")
                    
                    if percentage >= 90:
                        print("🎉 EXCELLENT! Comprehensive analysis with all key financial details!")
                    elif percentage >= 75:
                        print("👍 VERY GOOD! Analysis includes most important financial details!")
                    elif percentage >= 60:
                        print("👌 GOOD! Analysis has solid financial information!")
                    elif percentage >= 40:
                        print("⚠️ PARTIAL! Analysis missing some key financial details!")
                    else:
                        print("❌ POOR! Analysis lacks critical financial information!")
                    
                    # Special check for table extraction success
                    if any(keyword in answer.lower() for keyword in ['table', 'breakdown', 'detailed', 'commission']):
                        print("✅ Enhanced table extraction appears to be working!")
                    else:
                        print("❓ Table extraction may need further improvement")
                        
                else:
                    print(f"❌ Analysis failed: {result.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_docker_analysis()
