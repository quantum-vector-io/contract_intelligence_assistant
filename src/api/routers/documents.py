"""
Document indexing API router.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
import logging
import tempfile
import os

from src.services.document_indexing_service import DocumentIndexingService, index_sample_documents
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize document indexing service
indexing_service = DocumentIndexingService()


class TextIndexRequest(BaseModel):
    """Request model for indexing raw text."""
    text: str
    title: Optional[str] = None
    document_type: Optional[str] = "general"
    partner_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """Request model for search."""
    query: str
    size: Optional[int] = 10
    search_type: Optional[str] = "hybrid"  # "text", "semantic", or "hybrid"


@router.post("/upload")
async def upload_and_index_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    document_type: Optional[str] = Form("general"),
    partner_name: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Upload and index a document file.
    
    Supports PDF and text files.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.txt', '.md']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported types: .pdf, .txt, .md"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Write uploaded file to temp location
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Prepare metadata
            metadata = {
                "title": title or file.filename,
                "document_type": document_type,
                "partner_name": partner_name,
                "original_filename": file.filename,
                "file_size": len(content)
            }
            
            # Index the file
            result = indexing_service.index_file(temp_file_path, metadata)
            
            return {
                "status": "success",
                "message": "File uploaded and indexed successfully",
                "filename": file.filename,
                "indexing_result": result
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload and index file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index-text")
async def index_text(request: TextIndexRequest) -> Dict[str, Any]:
    """
    Index raw text content.
    """
    try:
        # Prepare metadata
        metadata = {
            "title": request.title or "Text Input",
            "document_type": request.document_type,
            "partner_name": request.partner_name
        }
        
        if request.metadata:
            metadata.update(request.metadata)
        
        # Index the text
        result = indexing_service.index_text(request.text, metadata)
        
        return {
            "status": "success",
            "message": "Text indexed successfully",
            "indexing_result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to index text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_documents(request: SearchRequest) -> Dict[str, Any]:
    """
    Search indexed documents.
    
    Supports text search, semantic search, and hybrid search.
    """
    try:
        if request.search_type == "semantic":
            results = indexing_service.semantic_search(request.query, request.size)
        elif request.search_type == "text":
            # Use the basic OpenSearch service for text-only search
            opensearch_results = indexing_service.opensearch_service.search_documents(
                request.query, request.size
            )
            results = {
                "status": "success",
                "query": request.query,
                "total_results": opensearch_results["hits"]["total"]["value"],
                "results": [
                    {
                        "id": hit["_id"],
                        "score": hit["_score"],
                        "content": hit["_source"].get("content", ""),
                        "metadata": {
                            "document_type": hit["_source"].get("document_type"),
                            "partner_name": hit["_source"].get("partner_name"),
                            "title": hit["_source"].get("title"),
                            "chunk_number": hit["_source"].get("chunk_number")
                        }
                    }
                    for hit in opensearch_results["hits"]["hits"]
                ]
            }
        else:  # hybrid (default)
            results = indexing_service.hybrid_search(request.query, request.size)
        
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_indexing_statistics() -> Dict[str, Any]:
    """
    Get statistics about indexed documents.
    """
    try:
        stats = indexing_service.get_indexing_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get indexing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index-samples")
async def index_sample_documents_endpoint() -> Dict[str, Any]:
    """
    Index sample documents from the data/sample_contracts directory.
    
    This is useful for testing and demonstration purposes.
    """
    try:
        # Ensure index exists first
        indexing_service.opensearch_service.create_index()
        
        # Index sample documents
        result = index_sample_documents()
        
        return {
            "status": "success",
            "message": "Sample documents indexed successfully",
            "indexing_result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to index sample documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear-index")
async def clear_index() -> Dict[str, Any]:
    """
    Clear all documents from the index.
    
    WARNING: This will delete all indexed documents!
    """
    try:
        # Delete and recreate the index
        success_delete = indexing_service.opensearch_service.delete_index()
        success_create = indexing_service.opensearch_service.create_index()
        
        if success_delete and success_create:
            return {
                "status": "success",
                "message": "Index cleared successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear index")
            
    except Exception as e:
        logger.error(f"Failed to clear index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/embedding")
async def test_embedding_service() -> Dict[str, Any]:
    """
    Health check for the embedding service connection.
    
    Tests connectivity to OpenAI's embedding API and validates
    that the service is operational for document processing.
    """
    try:
        connection_ok = indexing_service.embedding_service.test_connection()
        
        if connection_ok:
            return {
                "status": "success",
                "message": "Embedding service is working correctly",
                "model": indexing_service.embedding_service.model
            }
        else:
            return {
                "status": "error",
                "message": "Embedding service connection failed"
            }
            
    except Exception as e:
        logger.error(f"Embedding service health check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
