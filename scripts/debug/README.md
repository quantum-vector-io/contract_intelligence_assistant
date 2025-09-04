# Debug Scripts

This directory contains debugging and testing scripts used during development.

## Scripts Overview

### Database Checking
- `check_indexed_docs.py` - Check what documents are indexed and their metadata
- `check_partners.py` - Basic OpenSearch query to check partner data
- `reindex_documents.py` - Utility to reindex documents

### PDF Processing
- `check_pdf_extraction.py` - Test PDF content extraction with table handling

### API Testing  
- `quick_api_test.py` - Quick API testing script
- `test_simple_query.py` - Test simple vs complex query handling

### Context & Analysis Testing
- `debug_context_creation.py` - Debug context creation logic
- `test_direct_rag.py` - Direct RAG testing
- `test_docker_analysis.py` - Docker environment testing
- `test_final_analysis.py` - Final analysis testing
- `test_financial_analysis_api.py` - Financial analysis API testing
- `test_multi_doc_fix.py` - Multi-document analysis fix testing
- `test_payout_processing.py` - Payout processing testing
- `test_rag_discrepancy.py` - RAG discrepancy analysis testing
- `test_task3_workflow.py` - Task 3 workflow testing

## Usage

These scripts were used during development for debugging and testing specific features. They can be run individually for troubleshooting if needed.

**Note**: These scripts may require the main application services (OpenSearch, API) to be running.
