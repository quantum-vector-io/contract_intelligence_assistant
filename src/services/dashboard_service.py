"""
Dashboard service for Contract Intelligence Assistant metrics and analytics.

This module provides comprehensive business intelligence services for the
dashboard, aggregating data from various sources including OpenSearch,
document processing services, and system health metrics. It delivers
real-time insights into contract analysis performance, partner statistics,
and operational metrics.

The service abstracts complex data aggregation operations and provides
clean APIs for dashboard visualization components.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import asyncio

from src.services.opensearch_service import OpenSearchService
from src.core.config import settings

logger = logging.getLogger(__name__)


class DashboardService:
    """Comprehensive dashboard analytics and metrics service.
    
    This service provides business intelligence capabilities for the Contract
    Intelligence Assistant platform, aggregating data from multiple sources
    to deliver actionable insights through dashboard visualizations.
    
    Attributes:
        opensearch_service (OpenSearchService): Service for document queries.
        _cache (Dict): In-memory cache for performance optimization.
        _cache_ttl (int): Cache time-to-live in seconds.
    """
    
    def __init__(self, opensearch_service: OpenSearchService = None):
        """Initialize dashboard service with required dependencies.
        
        Args:
            opensearch_service: Optional OpenSearch service instance.
        """
        self.opensearch_service = opensearch_service or OpenSearchService()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes cache
        
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid.
        
        Args:
            cache_key: Key to check in cache.
            
        Returns:
            bool: True if cache is valid, False otherwise.
        """
        if cache_key not in self._cache:
            return False
            
        cache_time = self._cache[cache_key].get('timestamp', 0)
        return (datetime.now().timestamp() - cache_time) < self._cache_ttl
    
    def _get_cached_or_compute(self, cache_key: str, compute_func) -> Any:
        """Get cached data or compute and cache new data.
        
        Args:
            cache_key: Cache key for the data.
            compute_func: Function to compute data if not cached.
            
        Returns:
            Any: Cached or newly computed data.
        """
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]['data']
        
        try:
            data = compute_func()
            self._cache[cache_key] = {
                'data': data,
                'timestamp': datetime.now().timestamp()
            }
            return data
        except Exception as e:
            logger.error(f"Error computing data for {cache_key}: {e}")
            return {}
    
    async def get_document_overview(self) -> Dict[str, Any]:
        """Get comprehensive document processing overview.
        
        Returns:
            Dict containing document counts, types, and processing status.
        """
        def compute_overview():
            try:
                # Get total document count
                total_docs = self.opensearch_service.get_document_count()
                
                # Get document type breakdown
                doc_types = self._get_document_type_breakdown()
                
                # Get partner coverage
                partner_stats = self._get_partner_statistics()
                
                # Get recent activity
                recent_activity = self._get_recent_document_activity()
                
                return {
                    "total_documents": total_docs,
                    "document_types": doc_types,
                    "partner_statistics": partner_stats,
                    "recent_activity": recent_activity,
                    "last_updated": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error computing document overview: {e}")
                return {
                    "total_documents": 0,
                    "document_types": {},
                    "partner_statistics": {},
                    "recent_activity": [],
                    "error": str(e)
                }
        
        return self._get_cached_or_compute("document_overview", compute_overview)
    
    def _get_document_type_breakdown(self) -> Dict[str, int]:
        """Get breakdown of documents by type.
        
        Returns:
            Dict with document type counts.
        """
        try:
            # Query for document types aggregation
            search_body = {
                "size": 0,
                "aggs": {
                    "document_types": {
                        "terms": {
                            "field": "document_type",
                            "size": 20
                        }
                    }
                }
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            doc_types = {}
            if 'aggregations' in response:
                buckets = response['aggregations']['document_types']['buckets']
                for bucket in buckets:
                    doc_types[bucket['key']] = bucket['doc_count']
            
            # Add default types if not present
            default_types = ['contract', 'payout_report', 'addendum']
            for doc_type in default_types:
                if doc_type not in doc_types:
                    doc_types[doc_type] = 0
            
            return doc_types
            
        except Exception as e:
            logger.error(f"Error getting document type breakdown: {e}")
            return {"contract": 0, "payout_report": 0, "addendum": 0}
    
    def _get_partner_statistics(self) -> Dict[str, Any]:
        """Get partner-related statistics.
        
        Returns:
            Dict with partner analytics data.
        """
        try:
            # Query for partner aggregation
            search_body = {
                "size": 0,
                "aggs": {
                    "partners": {
                        "terms": {
                            "field": "partner_name",
                            "size": 50
                        }
                    },
                    "unique_partners": {
                        "cardinality": {
                            "field": "partner_name"
                        }
                    }
                }
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            partner_docs = {}
            total_partners = 0
            
            if 'aggregations' in response:
                # Partner document counts
                buckets = response['aggregations']['partners']['buckets']
                for bucket in buckets:
                    partner_docs[bucket['key']] = bucket['doc_count']
                
                # Unique partner count
                total_partners = response['aggregations']['unique_partners']['value']
            
            # Calculate coverage metrics
            partners_with_contracts = len([p for p, count in partner_docs.items() if count > 0])
            
            return {
                "total_partners": total_partners,
                "partners_with_documents": partners_with_contracts,
                "top_partners": dict(list(partner_docs.items())[:10]),
                "coverage_percentage": (partners_with_contracts / max(total_partners, 1)) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting partner statistics: {e}")
            return {
                "total_partners": 0,
                "partners_with_documents": 0,
                "top_partners": {},
                "coverage_percentage": 0
            }
    
    def _get_recent_document_activity(self) -> List[Dict[str, Any]]:
        """Get recent document processing activity.
        
        Returns:
            List of recent document activities.
        """
        try:
            # Get documents from last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            search_body = {
                "query": {
                    "range": {
                        "created_at": {
                            "gte": thirty_days_ago.isoformat()
                        }
                    }
                },
                "sort": [
                    {"created_at": {"order": "desc"}}
                ],
                "size": 50,
                "_source": ["title", "document_type", "partner_name", "created_at"]
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            activities = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                activities.append({
                    "title": source.get('title', 'Unknown Document'),
                    "type": source.get('document_type', 'unknown'),
                    "partner": source.get('partner_name', 'Unknown Partner'),
                    "created_at": source.get('created_at', ''),
                    "id": hit['_id']
                })
            
            return activities
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    async def get_financial_metrics(self) -> Dict[str, Any]:
        """Get financial analysis and discrepancy metrics.
        
        Returns:
            Dict with financial analytics data.
        """
        def compute_financial_metrics():
            try:
                # Search for financial documents
                financial_docs = self._get_financial_document_analysis()
                
                # Calculate discrepancy metrics
                discrepancy_stats = self._calculate_discrepancy_statistics()
                
                # Get commission analysis
                commission_analysis = self._get_commission_analysis()
                
                return {
                    "financial_documents": financial_docs,
                    "discrepancy_statistics": discrepancy_stats,
                    "commission_analysis": commission_analysis,
                    "last_updated": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error computing financial metrics: {e}")
                return {
                    "financial_documents": {},
                    "discrepancy_statistics": {},
                    "commission_analysis": {},
                    "error": str(e)
                }
        
        return self._get_cached_or_compute("financial_metrics", compute_financial_metrics)
    
    def _get_financial_document_analysis(self) -> Dict[str, Any]:
        """Analyze financial document distribution.
        
        Returns:
            Dict with financial document analytics.
        """
        try:
            # Query for contracts with financial terms
            search_body = {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"content": "commission"}},
                            {"match": {"content": "payout"}},
                            {"match": {"content": "payment"}},
                            {"match": {"content": "revenue"}}
                        ]
                    }
                },
                "size": 0,
                "aggs": {
                    "partner_financial_docs": {
                        "terms": {
                            "field": "partner_name",
                            "size": 20
                        }
                    }
                }
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            total_financial_docs = response['hits']['total']['value']
            partner_breakdown = {}
            
            if 'aggregations' in response:
                buckets = response['aggregations']['partner_financial_docs']['buckets']
                for bucket in buckets:
                    partner_breakdown[bucket['key']] = bucket['doc_count']
            
            return {
                "total_financial_documents": total_financial_docs,
                "partner_breakdown": partner_breakdown,
                "avg_docs_per_partner": total_financial_docs / max(len(partner_breakdown), 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial documents: {e}")
            return {
                "total_financial_documents": 0,
                "partner_breakdown": {},
                "avg_docs_per_partner": 0
            }
    
    def _calculate_discrepancy_statistics(self) -> Dict[str, Any]:
        """Calculate discrepancy detection statistics.
        
        Returns:
            Dict with discrepancy analytics.
        """
        # This would be enhanced with actual discrepancy data from analysis results
        # For now, providing mock structure that can be populated with real data
        return {
            "total_analyses_performed": 0,
            "discrepancies_detected": 0,
            "discrepancy_rate": 0.0,
            "avg_discrepancy_amount": 0.0,
            "most_common_discrepancy_types": []
        }
    
    def _get_commission_analysis(self) -> Dict[str, Any]:
        """Analyze commission structures across contracts.
        
        Returns:
            Dict with commission analytics.
        """
        try:
            # Search for commission-related content
            search_body = {
                "query": {
                    "match": {
                        "content": "commission"
                    }
                },
                "size": 100,
                "_source": ["content", "partner_name", "document_type"]
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            commission_partners = set()
            commission_types = Counter()
            
            for hit in response['hits']['hits']:
                source = hit['_source']
                partner = source.get('partner_name', 'Unknown')
                content = source.get('content', '').lower()
                
                if 'commission' in content:
                    commission_partners.add(partner)
                    
                    # Simple commission type detection
                    if 'percentage' in content or '%' in content:
                        commission_types['percentage'] += 1
                    if 'fixed' in content or 'flat' in content:
                        commission_types['fixed'] += 1
                    if 'tiered' in content or 'tier' in content:
                        commission_types['tiered'] += 1
            
            return {
                "partners_with_commission_data": len(commission_partners),
                "commission_structure_types": dict(commission_types),
                "total_commission_documents": len(response['hits']['hits'])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing commission data: {e}")
            return {
                "partners_with_commission_data": 0,
                "commission_structure_types": {},
                "total_commission_documents": 0
            }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics.
        
        Returns:
            Dict with system health and performance data.
        """
        def compute_system_health():
            try:
                # OpenSearch health
                opensearch_health = self.opensearch_service.health_check()
                
                # API health (basic check)
                api_health = self._check_api_health()
                
                # Performance metrics
                performance_metrics = self._get_performance_metrics()
                
                return {
                    "opensearch": opensearch_health,
                    "api": api_health,
                    "performance": performance_metrics,
                    "overall_status": self._calculate_overall_health_status(
                        opensearch_health, api_health
                    ),
                    "last_checked": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error computing system health: {e}")
                return {
                    "opensearch": {"status": "error"},
                    "api": {"status": "error"},
                    "performance": {},
                    "overall_status": "unhealthy",
                    "error": str(e)
                }
        
        return self._get_cached_or_compute("system_health", compute_system_health)
    
    def _check_api_health(self) -> Dict[str, Any]:
        """Check API service health.
        
        Returns:
            Dict with API health status.
        """
        return {
            "status": "healthy",
            "service": "fastapi",
            "version": settings.app_version,
            "debug_mode": settings.debug
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics.
        
        Returns:
            Dict with performance data.
        """
        try:
            # Get index statistics
            index_stats = self.opensearch_service.client.indices.stats(
                index=self.opensearch_service.index_name
            )
            
            # Extract relevant metrics
            total_docs = 0
            index_size = 0
            
            if 'indices' in index_stats:
                index_data = index_stats['indices'].get(
                    self.opensearch_service.index_name, {}
                )
                
                if 'total' in index_data:
                    docs_data = index_data['total'].get('docs', {})
                    store_data = index_data['total'].get('store', {})
                    
                    total_docs = docs_data.get('count', 0)
                    index_size = store_data.get('size_in_bytes', 0)
            
            return {
                "total_documents_indexed": total_docs,
                "index_size_bytes": index_size,
                "index_size_mb": round(index_size / (1024 * 1024), 2),
                "avg_document_size_kb": round(
                    (index_size / max(total_docs, 1)) / 1024, 2
                ) if total_docs > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "total_documents_indexed": 0,
                "index_size_bytes": 0,
                "index_size_mb": 0,
                "avg_document_size_kb": 0
            }
    
    def _calculate_overall_health_status(
        self, 
        opensearch_health: Dict[str, Any], 
        api_health: Dict[str, Any]
    ) -> str:
        """Calculate overall system health status.
        
        Args:
            opensearch_health: OpenSearch health data.
            api_health: API health data.
            
        Returns:
            str: Overall health status.
        """
        opensearch_ok = opensearch_health.get('status') in ['green', 'yellow']
        api_ok = api_health.get('status') == 'healthy'
        
        if opensearch_ok and api_ok:
            return "healthy"
        elif opensearch_ok or api_ok:
            return "degraded"
        else:
            return "unhealthy"
    
    async def get_query_analytics(self) -> Dict[str, Any]:
        """Get query and usage analytics.
        
        Returns:
            Dict with query analytics data.
        """
        # This would be enhanced with actual query logging
        # For now, providing mock structure
        return {
            "total_queries_today": 0,
            "avg_response_time_ms": 0,
            "most_common_query_types": [],
            "query_success_rate": 100.0,
            "peak_usage_hours": [],
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """Get all dashboard data in a single call for efficiency.
        
        Returns:
            Dict containing all dashboard metrics and analytics.
        """
        try:
            # Gather all data concurrently for better performance
            document_overview, financial_metrics, system_health, query_analytics = await asyncio.gather(
                self.get_document_overview(),
                self.get_financial_metrics(),
                self.get_system_health(),
                self.get_query_analytics(),
                return_exceptions=True
            )
            
            return {
                "document_overview": document_overview if not isinstance(document_overview, Exception) else {},
                "financial_metrics": financial_metrics if not isinstance(financial_metrics, Exception) else {},
                "system_health": system_health if not isinstance(system_health, Exception) else {},
                "query_analytics": query_analytics if not isinstance(query_analytics, Exception) else {},
                "generated_at": datetime.now().isoformat(),
                "cache_status": {
                    "document_overview": self._is_cache_valid("document_overview"),
                    "financial_metrics": self._is_cache_valid("financial_metrics"),
                    "system_health": self._is_cache_valid("system_health")
                }
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive dashboard data: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }