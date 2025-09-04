#!/usr/bin/env python3
"""
Check the actual content of the PDF payout report to see what's being extracted,
now with enhanced table handling.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.langchain_document_service import LangChainDocumentProcessor

def check_pdf_content():
    """Check what content is actually being extracted from the PDF."""
    print("🔍 Checking PDF Content Extraction with Enhanced Table Handling")
    print("==============================================================")
    
    pdf_path = "data/sample_contracts/4a_SushiExpress24-7_PayoutReport_2024-07-21.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"📄 Analyzing: {pdf_path}")
    
    try:
        # Initialize document processor
        processor = LangChainDocumentProcessor()
        
        # Process the PDF
        documents = processor.process_file_for_rag(pdf_path)
        
        print(f"📊 Found {len(documents)} document chunks")
        print()
        
        for i, doc in enumerate(documents[:3]):  # Show first 3 chunks
            print(f"🔸 Chunk {i+1}:")
            print(f"   Length: {len(doc.page_content)} characters")
            print(f"   Content preview: {doc.page_content[:300]}...")
            print()
        
        # Check for key financial information
        full_content = " ".join([doc.page_content for doc in documents])
        
        print("🔍 Financial Data Analysis:")
        # Check for the amount with and without spaces
        if "$1,902.95" in full_content or "1902.95" in full_content or "$1, 902. 95" in full_content:
            print("✅ Found $1,902.95 in extracted content")
        else:
            print("❌ $1,902.95 NOT found in extracted content")
        
        if "Total Earnings" in full_content or "Net Payout" in full_content:
            print("✅ Found earnings information")
        else:
            print("❌ Earnings information NOT found")
        
        if "[TABLE" in full_content:
            print("✅ Found table structures in extracted content")
        else:
            print("❌ No table structures detected")
        
        # Check for commission details
        if "commission" in full_content.lower() and ("28%" in full_content or "20%" in full_content):
            print("✅ Found commission details")
        else:
            print("❌ Commission details not clearly extracted")
        
        print()
        print("📝 FULL EXTRACTED CONTENT:")
        print("=" * 100)
        print(full_content)
        print("=" * 100)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_pdf_content()
