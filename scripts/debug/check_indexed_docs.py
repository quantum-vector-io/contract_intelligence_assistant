"""
Check what documents are indexed and their metadata.
"""
from src.services.opensearch_service import OpenSearchService

def check_indexed_documents():
    """Check what documents are actually in the index."""
    print("📊 Checking Indexed Documents")
    print("=" * 40)
    
    os_service = OpenSearchService()
    
    try:
        # Search for all documents
        search_body = {
            'size': 10,
            'query': {'match_all': {}},
            '_source': ['partner_name', 'partner_id', 'document_type', 'content']
        }
        
        response = os_service.client.search(index=os_service.index_name, body=search_body)
        
        print(f"📄 Total documents found: {response['hits']['total']['value']}")
        print()
        
        for i, hit in enumerate(response['hits']['hits']):
            source = hit['_source']
            print(f"Document {i+1}:")
            print(f"  Partner Name: {source.get('partner_name', 'N/A')}")
            print(f"  Partner ID: {source.get('partner_id', 'N/A')}")
            print(f"  Document Type: {source.get('document_type', 'N/A')}")
            content_preview = source.get('content', '')[:100].replace('\n', ' ')
            print(f"  Content Preview: {content_preview}...")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_indexed_documents()
