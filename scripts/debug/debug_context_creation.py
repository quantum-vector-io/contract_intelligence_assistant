#!/usr/bin/env python3
"""
Debug script to see exactly what context is being created for the AI.
This will help us understand why the AI says it can't see the payout report.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.rag_service import FinancialAnalystRAGChain
from src.services.document_indexing_service import DocumentIndexingService
import tempfile
import uuid

def test_context_creation():
    """Test what context is being created for the Sushi Express analysis."""
    print("🔍 Testing Context Creation for Multi-Document Analysis")
    print("=====================================================")
    
    # Initialize services
    indexing_service = DocumentIndexingService()
    rag_chain = FinancialAnalystRAGChain()
    
    # File paths
    contract_path = "data/sample_contracts/4_SkipTheDishesCA_SushiExpress24-7_RestaurantServicesAgreement_2022-03-10.pdf"
    payout_path = "data/sample_contracts/4a_SushiExpress24-7_PayoutReport_2024-07-21.pdf"
    
    if not os.path.exists(contract_path) or not os.path.exists(payout_path):
        print("❌ Files not found")
        return
    
    # Generate session info
    session_id = str(uuid.uuid4())[:8]
    partner_name = "Sushi Express 24/7"
    partner_id = "sushi_express_247"
    
    print(f"📊 Session ID: {session_id}")
    print(f"🏢 Partner: {partner_name}")
    print()
    
    try:
        # Index both documents
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
        
        # Refresh index
        indexing_service.opensearch_service.client.indices.refresh(index="financial_documents")
        print("🔄 Index refreshed")
        print()
        
        # Test context creation
        question = "Analyze the 'Sushi Express 24/7' contract and their latest payout report. How was the $1,902.95 payout calculated?"
        
        print("🧠 Creating retrieval context...")
        context = rag_chain.create_retrieval_context(partner_name, question, max_docs=15)
        
        print(f"📊 Context length: {len(context)} characters")
        print()
        print("📝 GENERATED CONTEXT:")
        print("=" * 80)
        print(context)
        print("=" * 80)
        
        # Check what document types are in the context
        contract_count = context.lower().count("(contract)")
        payout_count = context.lower().count("(payout_report)")
        
        print()
        print(f"📊 Context Analysis:")
        print(f"   Contract chunks: {contract_count}")
        print(f"   Payout chunks: {payout_count}")
        
        # Check if payout details are present
        if "$1,902.95" in context or "1902.95" in context:
            print("   ✅ Found specific payout amount in context")
        else:
            print("   ❌ Specific payout amount NOT found in context")
        
        if any(keyword in context.lower() for keyword in ['total earnings', 'total deductions', 'net payout', 'statement of earnings']):
            print("   ✅ Found payout report keywords in context")
        else:
            print("   ❌ Payout report keywords NOT found in context")
            
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
    test_context_creation()
