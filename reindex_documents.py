"""
Re-index all sample documents with enhanced PDF processing.
"""
import os
import glob
from src.services.document_indexing_service import DocumentIndexingService

def reindex_all_documents():
    """Re-index all sample documents from scratch."""
    print("🔄 Re-indexing all documents with enhanced PDF processing")
    print("=" * 60)
    
    # Initialize indexing service
    indexing_service = DocumentIndexingService()
    
    # Create index first
    print("📝 Creating fresh OpenSearch index...")
    index_created = indexing_service.opensearch_service.create_index()
    print(f"✅ Index creation result: {index_created}")
    
    # Find all PDF files in sample_contracts
    pdf_files = glob.glob("data/sample_contracts/*.pdf")
    txt_files = glob.glob("data/sample_contracts/*.txt")
    
    all_files = pdf_files + txt_files
    print(f"📁 Found {len(all_files)} files to index")
    
    total_chunks = 0
    successful_files = 0
    
    for file_path in all_files:
        try:
            print(f"\n📄 Processing: {os.path.basename(file_path)}")
            
            # Extract metadata from filename
            filename = os.path.basename(file_path)
            metadata = {
                "filename": filename,
                "file_path": file_path,
                "processing_timestamp": "2024-09-04T00:00:00Z"
            }
            
            # Determine document type and partner info
            if "Partnership" in filename or "Agreement" in filename or "Contract" in filename:
                metadata["document_type"] = "contract"
            elif "Payout" in filename or "Report" in filename:
                metadata["document_type"] = "payout_report"
            
            # Extract partner name
            if "SushiExpress" in filename or "Sushi" in filename:
                metadata["partner_name"] = "Sushi Express 24/7"
                metadata["partner_id"] = "sushi_express_247"
            elif "GoldenFork" in filename:
                metadata["partner_name"] = "The Golden Fork Pizzeria"
                metadata["partner_id"] = "golden_fork_pizzeria"
            elif "SchnitzelHaus" in filename:
                metadata["partner_name"] = "SchnitzelHaus"
                metadata["partner_id"] = "schnitzel_haus"
            elif "UrbanSpice" in filename:
                metadata["partner_name"] = "Urban Spice Group"
                metadata["partner_id"] = "urban_spice_group"
            
            # Index the file
            result = indexing_service.index_file(file_path, metadata)
            
            print(f"✅ Successfully indexed: {result.get('chunks_indexed', 0)} chunks")
            total_chunks += result.get('chunks_indexed', 0)
            successful_files += 1
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
    
    print(f"\n🎉 Indexing Complete!")
    print(f"📊 Files processed: {successful_files}/{len(all_files)}")
    print(f"📄 Total chunks indexed: {total_chunks}")
    
    # Verify indexing
    print(f"\n🔍 Verifying index...")
    try:
        count = indexing_service.opensearch_service.get_document_count()
        print(f"✅ Documents in index: {count}")
    except Exception as e:
        print(f"❌ Error checking document count: {e}")

if __name__ == "__main__":
    reindex_all_documents()
