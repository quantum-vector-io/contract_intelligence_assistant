#!/usr/bin/env python3
"""
Direct test of the RAG context creation to see if our fix is working.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.rag_service import FinancialAnalystRAGChain
from src.services.document_indexing_service import DocumentIndexingService
import tempfile
import uuid
import time

def test_direct_rag():
    """Test RAG service directly with fresh upload."""
    print("🔍 Direct RAG Test with Fresh Upload")
    print("===================================")
    
    # Initialize services
    indexing_service = DocumentIndexingService()
    rag_chain = FinancialAnalystRAGChain()
    
    # File paths
    contract_path = "data/sample_contracts/4_SkipTheDishesCA_SushiExpress24-7_RestaurantServicesAgreement_2022-03-10.pdf"
    payout_path = "data/sample_contracts/4a_SushiExpress24-7_PayoutReport_2024-07-21.pdf"
    
    if not os.path.exists(contract_path) or not os.path.exists(payout_path):
        print("❌ Files not found")
        return
    
    # Generate unique session info
    session_id = str(uuid.uuid4())[:8]
    partner_name = "Sushi Express 24/7"
    partner_id = "sushi_express_247"
    
    print(f"📊 Session ID: {session_id}")
    print(f"🏢 Partner: {partner_name}")
    print()
    
    try:
        # Index both documents with fresh session
        print("📄 Indexing contract document...")
        with open(contract_path, 'rb') as f:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(f.read())
                contract_temp_path = temp_file.name
        
        contract_metadata = {
            "partner_name": partner_name,
            "document_type": "contract",
            "partner_id": partner_id,
            "original_filename": os.path.basename(contract_path),
            "session_id": session_id
        }
        
        contract_result = indexing_service.index_file(contract_temp_path, contract_metadata)
        print(f"   Result: {contract_result.get('status')}")
        
        print("💰 Indexing payout document...")
        with open(payout_path, 'rb') as f:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(f.read())
                payout_temp_path = temp_file.name
        
        payout_metadata = {
            "partner_name": partner_name,
            "document_type": "payout_report",
            "partner_id": partner_id,
            "original_filename": os.path.basename(payout_path),
            "session_id": session_id
        }
        
        payout_result = indexing_service.index_file(payout_temp_path, payout_metadata)
        print(f"   Result: {payout_result.get('status')}")
        
        # Refresh index and wait
        indexing_service.opensearch_service.client.indices.refresh(index="financial_documents")
        time.sleep(2)  # Give more time for indexing
        print("🔄 Index refreshed")
        print()
        
        # Test context creation with our fix
        question = "How was the $1,902.95 payout calculated?"
        
        print("🧠 Creating retrieval context with enhanced logic...")
        context = rag_chain.create_retrieval_context(partner_name, question, max_docs=10)
        
        print(f"📊 Context length: {len(context)} characters")
        
        # Check what's in the context
        if "$1,902.95" in context or "1902.95" in context:
            print("✅ Found $1,902.95 in context!")
        else:
            print("❌ $1,902.95 NOT found in context")
        
        if "(CONTRACT)" in context and "(PAYOUT_REPORT)" in context:
            print("✅ Both document types included in context")
        else:
            print("❌ Missing document types in context")
        
        # Show sample of context
        print()
        print("📝 CONTEXT SAMPLE (first 500 chars):")
        print("-" * 50)
        print(context[:500] + "...")
        print("-" * 50)
        
        # Now test the actual analysis
        print()
        print("🤖 Running discrepancy analysis...")
        analysis = rag_chain.analyze_contract_discrepancies(partner_name, question, detailed_report=False)
        
        print()
        print("🎯 ANALYSIS RESULT:")
        print("=" * 80)
        print(analysis)
        print("=" * 80)
        
        # Check if analysis includes payout details
        if "$1,902.95" in analysis or "1902.95" in analysis:
            print("✅ SUCCESS: Analysis includes specific payout amount!")
        else:
            print("❌ ISSUE: Analysis doesn't include specific payout amount")
        
        if any(keyword in analysis.lower() for keyword in ['commission', 'service fee', 'deduction', 'total gross sales']):
            print("✅ SUCCESS: Analysis includes detailed financial breakdown!")
        else:
            print("❌ ISSUE: Analysis lacks detailed financial breakdown")
            
        # Clean up temp files
        try:
            os.unlink(contract_temp_path)
            os.unlink(payout_temp_path)
        except:
            pass
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_rag()
