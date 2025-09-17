"""
Dashboard API router for Contract Intelligence Assistant analytics endpoints.

This module provides RESTful API endpoints for dashboard data, metrics,
and analytics. It serves real-time business intelligence data to the
frontend dashboard components, including document statistics, financial
metrics, system health, and performance analytics.

The router integrates with the DashboardService to provide comprehensive
analytics capabilities with proper error handling and response formatting.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from src.services.dashboard_service import DashboardService
from src.services.opensearch_service import OpenSearchService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={
        404: {"description": "Dashboard data not found"},
        500: {"description": "Internal server error"}
    }
)

# Initialize services
opensearch_service = OpenSearchService()
dashboard_service = DashboardService(opensearch_service)


@router.get("/", summary="Dashboard Status")
async def dashboard_status():
    """Get dashboard service status and basic information.
    
    Returns:
        Dict: Dashboard service status and metadata.
    """
    try:
        return {
            "service": "dashboard",
            "status": "active",
            "version": "1.0.0",
            "description": "Contract Intelligence Assistant Dashboard Analytics",
            "endpoints": [
                "/dashboard/overview",
                "/dashboard/documents", 
                "/dashboard/financial",
                "/dashboard/health",
                "/dashboard/analytics",
                "/dashboard/comprehensive"
            ]
        }
    except Exception as e:
        logger.error(f"Dashboard status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview", summary="Dashboard Overview")
async def get_dashboard_overview():
    """Get high-level dashboard overview with key metrics.
    
    Returns:
        Dict: Overview metrics including document counts, partner stats,
              and recent activity summary.
    """
    try:
        overview_data = await dashboard_service.get_document_overview()
        
        if "error" in overview_data:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to get overview: {overview_data['error']}"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": overview_data,
                "message": "Dashboard overview retrieved successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", summary="Document Analytics")
async def get_document_analytics(
    include_recent: bool = Query(True, description="Include recent activity data"),
    partner_filter: str = Query(None, description="Filter by specific partner")
):
    """Get comprehensive document analytics and statistics.
    
    Args:
        include_recent: Whether to include recent activity data.
        partner_filter: Optional partner name filter.
    
    Returns:
        Dict: Document analytics including counts, types, and activity.
    """
    try:
        document_data = await dashboard_service.get_document_overview()
        
        if "error" in document_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get document analytics: {document_data['error']}"
            )
        
        # Apply partner filter if specified
        if partner_filter:
            # Filter recent activity by partner
            if include_recent and "recent_activity" in document_data:
                document_data["recent_activity"] = [
                    activity for activity in document_data["recent_activity"]
                    if partner_filter.lower() in activity.get("partner", "").lower()
                ]
            
            # Filter top partners
            if "partner_statistics" in document_data and "top_partners" in document_data["partner_statistics"]:
                top_partners = document_data["partner_statistics"]["top_partners"]
                filtered_partners = {
                    k: v for k, v in top_partners.items()
                    if partner_filter.lower() in k.lower()
                }
                document_data["partner_statistics"]["top_partners"] = filtered_partners
        
        # Remove recent activity if not requested
        if not include_recent and "recent_activity" in document_data:
            del document_data["recent_activity"]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": document_data,
                "filters_applied": {
                    "partner_filter": partner_filter,
                    "include_recent": include_recent
                },
                "message": "Document analytics retrieved successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financial", summary="Financial Metrics")
async def get_financial_metrics():
    """Get financial analysis metrics and discrepancy statistics.
    
    Returns:
        Dict: Financial metrics including document analysis, discrepancy
              statistics, and commission analysis.
    """
    try:
        financial_data = await dashboard_service.get_financial_metrics()
        
        if "error" in financial_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get financial metrics: {financial_data['error']}"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": financial_data,
                "message": "Financial metrics retrieved successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Financial metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="System Health")
async def get_system_health():
    """Get comprehensive system health and performance metrics.
    
    Returns:
        Dict: System health including OpenSearch status, API health,
              and performance metrics.
    """
    try:
        health_data = await dashboard_service.get_system_health()
        
        if "error" in health_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get system health: {health_data['error']}"
            )
        
        # Determine HTTP status based on overall health
        overall_status = health_data.get("overall_status", "unhealthy")
        http_status = 200 if overall_status in ["healthy", "degraded"] else 503
        
        return JSONResponse(
            status_code=http_status,
            content={
                "success": True,
                "data": health_data,
                "message": f"System health retrieved successfully - Status: {overall_status}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System health error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", summary="Query Analytics")
async def get_query_analytics():
    """Get query and usage analytics data.
    
    Returns:
        Dict: Query analytics including usage patterns, response times,
              and success rates.
    """
    try:
        analytics_data = await dashboard_service.get_query_analytics()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": analytics_data,
                "message": "Query analytics retrieved successfully"
            }
        )
    except Exception as e:
        logger.error(f"Query analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comprehensive", summary="Comprehensive Dashboard Data")
async def get_comprehensive_dashboard_data():
    """Get all dashboard data in a single optimized request.
    
    This endpoint provides all dashboard metrics in one call for efficient
    frontend loading and reduced API requests.
    
    Returns:
        Dict: Complete dashboard data including documents, financial metrics,
              system health, and analytics.
    """
    try:
        comprehensive_data = await dashboard_service.get_comprehensive_dashboard_data()
        
        if "error" in comprehensive_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get comprehensive data: {comprehensive_data['error']}"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": comprehensive_data,
                "message": "Comprehensive dashboard data retrieved successfully"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comprehensive dashboard data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary", summary="Quick Stats Summary")
async def get_quick_stats():
    """Get quick summary statistics for dashboard widgets.
    
    Returns:
        Dict: Quick stats including total documents, partners, and health status.
    """
    try:
        # Get basic counts quickly
        total_docs = dashboard_service.opensearch_service.get_document_count()
        
        # Get basic health check
        opensearch_health = dashboard_service.opensearch_service.health_check()
        health_status = opensearch_health.get('status', 'unknown')
        
        # Quick partner count (from cache if available)
        partner_stats = {}
        if dashboard_service._is_cache_valid("document_overview"):
            cached_data = dashboard_service._cache["document_overview"]["data"]
            partner_stats = cached_data.get("partner_statistics", {})
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "total_documents": total_docs,
                    "total_partners": partner_stats.get("total_partners", 0),
                    "system_health": health_status,
                    "last_updated": dashboard_service._cache.get("document_overview", {}).get("timestamp", 0)
                },
                "message": "Quick stats retrieved successfully"
            }
        )
    except Exception as e:
        logger.error(f"Quick stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", summary="Refresh Dashboard Cache")
async def refresh_dashboard_cache():
    """Force refresh of dashboard cache for updated data.
    
    Returns:
        Dict: Cache refresh status and new data timestamps.
    """
    try:
        # Clear all cache entries
        dashboard_service._cache.clear()
        
        # Preload fresh data
        overview_data = await dashboard_service.get_document_overview()
        financial_data = await dashboard_service.get_financial_metrics()
        health_data = await dashboard_service.get_system_health()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "cache_cleared": True,
                    "data_refreshed": True,
                    "overview_updated": overview_data.get("last_updated"),
                    "financial_updated": financial_data.get("last_updated"),
                    "health_updated": health_data.get("last_checked")
                },
                "message": "Dashboard cache refreshed successfully"
            }
        )
    except Exception as e:
        logger.error(f"Cache refresh error: {e}")
        raise HTTPException(status_code=500, detail=str(e))