"""
Test script to isolate and debug the text processing of the payout report.
"""
import os
from src.services.document_service import DocumentProcessor

def test_payout_report_processing():
    """
    Processes only the payout report and prints the cleaned text to isolate
    any text extraction or cleaning issues.
    """
    print("🧪 Testing Payout Report Processing")
    print("=" * 40)
    
    payout_file_path = "data/sample_contracts/4a_SushiExpress24-7_PayoutReport_2024-07-21.pdf"
    
    if not os.path.exists(payout_file_path):
        print(f"❌ ERROR: Payout report not found at: {payout_file_path}")
        return
        
    try:
        # Initialize the document processor
        processor = DocumentProcessor()
        
        # Extract text from the PDF
        print(f"📄 Processing file: {payout_file_path}\n")
        extracted_text = processor._extract_pdf_text(payout_file_path)
        
        print("--- RAW EXTRACTED TEXT (before cleaning) ---")
        print(repr(extracted_text))
        print("-" * 40)
        
        # Clean the extracted text
        cleaned_text = processor._clean_extracted_text(extracted_text)
        
        print("\n--- CLEANED TEXT (after processing) ---")
        print(cleaned_text)
        print("-" * 40)
        
        print("\n✅ Test complete.")
        
    except Exception as e:
        print(f"🔥 An error occurred: {e}")

if __name__ == "__main__":
    test_payout_report_processing()
