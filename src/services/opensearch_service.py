"""
OpenSearch service for document indexing and search operations.

This module provides a comprehensive service layer for interacting with
OpenSearch clusters. It handles document indexing, search operations, index
management, and health monitoring for the Contract Intelligence Assistant
platform's document storage and retrieval capabilities.

The service abstracts OpenSearch client operations and provides a clean
interface for document operations with proper error handling and logging.
"""
import logging
from typing import Dict, List, Optional, Any
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import OpenSearchException

from src.core.config import settings

logger = logging.getLogger(__name__)


class OpenSearchService:
    """Service for comprehensive OpenSearch operations and document management.
    
    This service provides a high-level interface for OpenSearch operations
    including document indexing, search queries, index management, and health
    monitoring. It handles connection management, error handling, and provides
    optimized search capabilities for the document intelligence platform.
    
    Attributes:
        client (OpenSearch): Configured OpenSearch client instance.
        index_name (str): Default index name for document operations.
    """
    
    def __init__(self):
        """Initialize OpenSearch service with configured client and settings.
        
        Creates an OpenSearch client connection using application settings
        and prepares the service for document operations.
        """
        self.client = self._create_client()
        self.index_name = settings.opensearch_index_name
    
    def _create_client(self) -> OpenSearch:
        """Create and configure OpenSearch client with optimized settings.
        
        Establishes connection to OpenSearch cluster using application
        configuration with appropriate timeouts, retry policies, and
        connection parameters for reliable operation.
        
        Returns:
            OpenSearch: Configured OpenSearch client instance.
            
        Raises:
            Exception: When client initialization fails due to connection
                or configuration issues.
        """
        try:
            client = OpenSearch(
                hosts=[{
                    'host': settings.opensearch_host,
                    'port': settings.opensearch_port
                }],
                http_auth=None,  # No auth for local development
                use_ssl=False,
                verify_certs=False,
                connection_class=RequestsHttpConnection,
                timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
            
            logger.info(f"OpenSearch client initialized for {settings.opensearch_url}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenSearch client: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check OpenSearch cluster health and availability.
        
        Performs a health check on the OpenSearch cluster to verify
        connectivity and cluster status. This is essential for monitoring
        and ensuring service availability.
        
        Returns:
            Dict[str, Any]: Cluster health information including status,
                node counts, and performance metrics.
                
        Raises:
            OpenSearchException: When cluster is unreachable or unhealthy.
        """
        try:
            health = self.client.cluster.health()
            logger.info(f"OpenSearch health check: {health.get('status', 'unknown')}")
            return health
        except OpenSearchException as e:
            logger.error(f"OpenSearch health check failed: {e}")
            return {"status": "error", "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during health check: {e}")
            return {"status": "error", "error": str(e)}
    
    def create_index(self, index_name: Optional[str] = None) -> bool:
        """Create index with document mapping."""
        index_name = index_name or self.index_name
        
        # Define mapping for financial documents
        mapping = {
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "document_type": {
                        "type": "keyword"
                    },
                    "partner_name": {
                        "type": "keyword"
                    },
                    "contract_date": {
                        "type": "date"
                    },
                    "chunk_id": {
                        "type": "keyword"
                    },
                    "metadata": {
                        "type": "object"
                    },
                    "embedding": {
                        "type": "float",
                        "index": False
                    },
                    "created_at": {
                        "type": "date"
                    }
                }
            }
        }
        
        try:
            if not self.client.indices.exists(index=index_name):
                response = self.client.indices.create(
                    index=index_name,
                    body=mapping
                )
                logger.info(f"Created index '{index_name}': {response}")
                return True
            else:
                logger.info(f"Index '{index_name}' already exists")
                return True
                
        except OpenSearchException as e:
            logger.error(f"Failed to create index '{index_name}': {e}")
            return False
    
    def index_document(self, document: Dict[str, Any], doc_id: Optional[str] = None) -> bool:
        """Index a document."""
        try:
            response = self.client.index(
                index=self.index_name,
                body=document,
                id=doc_id,
                refresh=True
            )
            logger.info(f"Indexed document: {response.get('_id')}")
            return True
            
        except OpenSearchException as e:
            logger.error(f"Failed to index document: {e}")
            return False
    
    def search_documents(self, query: str, size: int = 10) -> Dict[str, Any]:
        """Search documents using text query."""
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "title", "partner_name"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            },
            "size": size,
            "sort": [
                {"_score": {"order": "desc"}}
            ]
        }
        
        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            logger.info(f"Search completed. Found {response['hits']['total']['value']} results")
            return response
            
        except OpenSearchException as e:
            logger.error(f"Search failed: {e}")
            return {"hits": {"hits": [], "total": {"value": 0}}}
    
    def delete_index(self, index_name: Optional[str] = None) -> bool:
        """Delete an index."""
        index_name = index_name or self.index_name
        
        try:
            if self.client.indices.exists(index=index_name):
                response = self.client.indices.delete(index=index_name)
                logger.info(f"Deleted index '{index_name}': {response}")
                return True
            else:
                logger.info(f"Index '{index_name}' does not exist")
                return True
                
        except OpenSearchException as e:
            logger.error(f"Failed to delete index '{index_name}': {e}")
            return False
    
    def get_document_count(self, index_name: Optional[str] = None) -> int:
        """Get total document count in index."""
        index_name = index_name or self.index_name
        
        try:
            response = self.client.count(index=index_name)
            count = response.get('count', 0)
            logger.info(f"Document count in '{index_name}': {count}")
            return count
            
        except OpenSearchException as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
