#!/usr/bin/env python3
"""
Test script to verify that simple database queries now return appropriate responses.
"""

import requests
import json
import time

def test_simple_query():
    """Test a simple database query for restaurant names."""
    url = "http://localhost:8000/query"
    
    # Test data - simple query that should NOT trigger financial analysis
    data = {
        "question": "tell me restaurant names in list from db"
    }
    
    print("Testing simple database query:")
    print(f"Question: {data['question']}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response received successfully")
            print(f"Response: {result['answer']}")
            
            # Check if response looks like a simple list vs complex financial analysis
            analysis_text = result['answer'].lower()
            
            # Complex analysis indicators
            complex_indicators = [
                'financial analysis', 'commission', 'reconciliation', 
                'discrepancy', 'payout calculation', 'analysis report'
            ]
            
            # Simple response indicators
            simple_indicators = [
                'restaurant', 'sushi express', 'list', 'available'
            ]
            
            has_complex = any(indicator in analysis_text for indicator in complex_indicators)
            has_simple = any(indicator in analysis_text for indicator in simple_indicators)
            
            if has_complex and not has_simple:
                print("❌ ISSUE: Response still looks like complex financial analysis")
                print("Contains complex analysis indicators")
            elif has_simple and not has_complex:
                print("✅ SUCCESS: Response looks like simple database information")
            else:
                print("⚠️  MIXED: Response contains both simple and complex elements")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False
        
    return True

def test_complex_query():
    """Test a complex query that should trigger financial analysis."""
    url = "http://localhost:8000/query"
    
    # Test data - complex query that SHOULD trigger financial analysis
    data = {
        "question": "analyze the payout discrepancies for Sushi Express"
    }
    
    print("\n" + "="*60)
    print("Testing complex analysis query:")
    print(f"Question: {data['question']}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response received successfully")
            
            # Check if response looks like complex financial analysis
            analysis_text = result['answer'].lower()
            
            complex_indicators = [
                'analysis', 'commission', 'calculation', 
                'discrepancy', 'payout', 'financial'
            ]
            
            has_complex = any(indicator in analysis_text for indicator in complex_indicators)
            
            if has_complex:
                print("✅ SUCCESS: Response contains appropriate complex analysis")
                print(f"First 200 chars: {result['answer'][:200]}...")
            else:
                print("❌ ISSUE: Complex query didn't trigger detailed analysis")
                print(f"Response: {result['answer']}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("Contract Intelligence Assistant - Query Type Testing")
    print("="*60)
    
    # Wait for services to be ready
    print("Waiting for services to start...")
    time.sleep(10)
    
    # Test simple query
    test_simple_query()
    
    # Test complex query
    test_complex_query()
    
    print("\n" + "="*60)
    print("Testing completed!")
