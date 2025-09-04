import requests
import json

def check_partners():
    try:
        r = requests.get('http://localhost:9200/financial_documents/_search', 
            json={'query': {'match_all': {}}, 'size': 5, '_source': ['partner_name', 'partner_id', 'document_type']})
        
        if r.status_code == 200:
            data = r.json()
            print(f"Total documents: {data['hits']['total']['value']}")
            print("\nFirst 5 documents:")
            for hit in data['hits']['hits']:
                source = hit['_source']
                print(f"Partner: '{source.get('partner_name')}', ID: '{source.get('partner_id')}', Type: '{source.get('document_type')}'")
        else:
            print(f"Error: {r.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_partners()
