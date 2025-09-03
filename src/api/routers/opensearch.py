"""
OpenSearch API router.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

from src.services.opensearch_service import OpenSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/opensearch", tags=["opensearch"])

# Initialize OpenSearch service
opensearch_service = OpenSearchService()


@router.get("/health")
async def opensearch_health() -> Dict[str, Any]:
    """Check OpenSearch cluster health."""
    try:
        health = opensearch_service.health_check()
        return {
            "status": "success",
            "data": health
        }
    except Exception as e:
        logger.error(f"OpenSearch health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/create")
async def create_index(index_name: Optional[str] = None) -> Dict[str, Any]:
    """Create OpenSearch index."""
    try:
        success = opensearch_service.create_index(index_name)
        if success:
            return {
                "status": "success",
                "message": f"Index '{index_name or opensearch_service.index_name}' created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create index")
    except Exception as e:
        logger.error(f"Failed to create index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/index")
async def delete_index(index_name: Optional[str] = None) -> Dict[str, Any]:
    """Delete OpenSearch index."""
    try:
        success = opensearch_service.delete_index(index_name)
        if success:
            return {
                "status": "success",
                "message": f"Index '{index_name or opensearch_service.index_name}' deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete index")
    except Exception as e:
        logger.error(f"Failed to delete index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_documents(
    q: str,
    size: int = 10
) -> Dict[str, Any]:
    """Search documents in OpenSearch."""
    try:
        if not q.strip():
            raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
        
        results = opensearch_service.search_documents(q, size)
        
        return {
            "status": "success",
            "data": {
                "total": results["hits"]["total"]["value"],
                "results": [
                    {
                        "id": hit["_id"],
                        "score": hit["_score"],
                        "source": hit["_source"]
                    }
                    for hit in results["hits"]["hits"]
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_index_stats() -> Dict[str, Any]:
    """Get OpenSearch index statistics."""
    try:
        document_count = opensearch_service.get_document_count()
        health = opensearch_service.health_check()
        
        return {
            "status": "success",
            "data": {
                "index_name": opensearch_service.index_name,
                "document_count": document_count,
                "cluster_status": health.get("status", "unknown"),
                "cluster_name": health.get("cluster_name", "unknown")
            }
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
