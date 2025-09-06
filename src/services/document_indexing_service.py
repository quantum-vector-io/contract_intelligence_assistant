"""
Complete document indexing service for processing and search integration.

This module provides a comprehensive service that combines document processing,
embedding generation, and OpenSearch indexing into a unified workflow. It
handles the complete pipeline from raw documents to searchable indexed content
with semantic embeddings.

The service orchestrates multiple components to process various document formats,
generate embeddings for semantic search, and store the results in OpenSearch
for retrieval and analysis operations.
"""
import logging
from typing import List, Dict, Any, Optional, Union
import os
from datetime import datetime

from src.services.document_service import DocumentProcessor
from src.services.embedding_service import EmbeddingService
from src.services.opensearch_service import OpenSearchService

logger = logging.getLogger(__name__)


class DocumentIndexingService:
    """Complete service for processing and indexing documents with embeddings.
    
    This service provides end-to-end document processing capabilities by
    combining document parsing, text chunking, embedding generation, and
    OpenSearch indexing into a single cohesive workflow.
    
    The service handles multiple document formats and ensures proper metadata
    association for enhanced search and retrieval operations.
    
    Attributes:
        document_processor (DocumentProcessor): Handles document parsing and chunking.
        embedding_service (EmbeddingService): Generates semantic embeddings.
        opensearch_service (OpenSearchService): Manages search index operations.
    """
    
    def __init__(self):
        """Initialize the document indexing service with required components.
        
        Sets up the document processor for file handling, embedding service
        for semantic vector generation, and OpenSearch service for indexing
        and retrieval operations.
        """
        self.document_processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        self.opensearch_service = OpenSearchService()
    
    def index_file(self, file_path: str, document_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process and index a single file with full pipeline processing.
        
        Executes the complete document indexing workflow including file parsing,
        text chunking, embedding generation, and OpenSearch storage. Provides
        comprehensive error handling and progress logging.
        
        Args:
            file_path (str): Absolute path to the file to process.
            document_metadata (Dict[str, Any], optional): Additional metadata
                to associate with the document for enhanced search and filtering.
                
        Returns:
            Dict[str, Any]: Indexing results containing processing statistics,
                chunk counts, and success/error information.
                
        Raises:
            ValueError: When no chunks are generated from the document.
            Exception: When document processing or indexing operations fail.
        """
        logger.info(f"Starting indexing process for file: {file_path}")
        
        try:
            # Step 1: Process document into chunks
            logger.info("Step 1: Processing document into chunks...")
            chunks = self.document_processor.process_file(file_path, document_metadata)
            
            if not chunks:
                raise ValueError("No chunks generated from document")
            
            logger.info(f"Generated {len(chunks)} chunks from document")
            
            # Step 2: Generate embeddings for chunks
            logger.info("Step 2: Generating embeddings...")
            chunks_with_embeddings = self.embedding_service.add_embeddings_to_chunks(chunks)
            
            # Step 3: Index chunks in OpenSearch
            logger.info("Step 3: Indexing chunks in OpenSearch...")
            indexed_count = 0
            failed_count = 0
            
            for chunk in chunks_with_embeddings:
                try:
                    success = self.opensearch_service.index_document(
                        document=chunk,
                        doc_id=chunk.get('chunk_id')
                    )
                    if success:
                        indexed_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Failed to index chunk {chunk.get('chunk_id', 'unknown')}: {e}")
                    failed_count += 1
            
            # Step 4: Return results
            result = {
                "status": "success",
                "file_path": file_path,
                "total_chunks": len(chunks),
                "indexed_chunks": indexed_count,
                "failed_chunks": failed_count,
                "processing_time": datetime.now().isoformat(),
                "document_metadata": document_metadata or {}
            }
            
            logger.info(f"Indexing completed: {indexed_count}/{len(chunks)} chunks indexed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to index file '{file_path}': {e}")
            return {
                "status": "error",
                "file_path": file_path,
                "error": str(e),
                "processing_time": datetime.now().isoformat()
            }
    
    def index_text(self, text: str, document_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process and index raw text.
        
        Args:
            text: Raw text content to process
            document_metadata: Additional metadata for the document
            
        Returns:
            Indexing results with statistics
        """
        logger.info("Starting indexing process for raw text")
        
        try:
            # Step 1: Process text into chunks
            logger.info("Step 1: Processing text into chunks...")
            chunks = self.document_processor.process_text(text, document_metadata)
            
            if not chunks:
                raise ValueError("No chunks generated from text")
            
            logger.info(f"Generated {len(chunks)} chunks from text")
            
            # Step 2: Generate embeddings for chunks
            logger.info("Step 2: Generating embeddings...")
            chunks_with_embeddings = self.embedding_service.add_embeddings_to_chunks(chunks)
            
            # Step 3: Index chunks in OpenSearch
            logger.info("Step 3: Indexing chunks in OpenSearch...")
            indexed_count = 0
            failed_count = 0
            
            for chunk in chunks_with_embeddings:
                try:
                    success = self.opensearch_service.index_document(
                        document=chunk,
                        doc_id=chunk.get('chunk_id')
                    )
                    if success:
                        indexed_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Failed to index chunk {chunk.get('chunk_id', 'unknown')}: {e}")
                    failed_count += 1
            
            # Step 4: Return results
            result = {
                "status": "success",
                "source": "text_input",
                "total_chunks": len(chunks),
                "indexed_chunks": indexed_count,
                "failed_chunks": failed_count,
                "processing_time": datetime.now().isoformat(),
                "document_metadata": document_metadata or {}
            }
            
            logger.info(f"Text indexing completed: {indexed_count}/{len(chunks)} chunks indexed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to index text: {e}")
            return {
                "status": "error",
                "source": "text_input",
                "error": str(e),
                "processing_time": datetime.now().isoformat()
            }
    
    def index_directory(self, directory_path: str, file_extensions: List[str] = None) -> Dict[str, Any]:
        """
        Process and index all files in a directory.
        
        Args:
            directory_path: Path to directory containing files
            file_extensions: List of file extensions to process (default: ['.txt', '.pdf'])
            
        Returns:
            Combined indexing results for all files
        """
        if file_extensions is None:
            file_extensions = ['.txt', '.pdf']
        
        logger.info(f"Starting bulk indexing for directory: {directory_path}")
        
        if not os.path.exists(directory_path):
            return {
                "status": "error",
                "error": f"Directory not found: {directory_path}",
                "processing_time": datetime.now().isoformat()
            }
        
        results = {
            "status": "success",
            "directory_path": directory_path,
            "processed_files": [],
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "total_indexed_chunks": 0,
            "processing_time": datetime.now().isoformat()
        }
        
        # Find all files with specified extensions
        files_to_process = []
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in file_extensions:
                    files_to_process.append(file_path)
        
        results["total_files"] = len(files_to_process)
        
        if not files_to_process:
            logger.warning(f"No files found with extensions {file_extensions} in {directory_path}")
            return results
        
        # Process each file
        for file_path in files_to_process:
            try:
                # Generate metadata based on filename
                filename = os.path.basename(file_path)
                doc_metadata = self._generate_metadata_from_filename(filename)
                
                # Index the file
                file_result = self.index_file(file_path, doc_metadata)
                
                # Update results
                results["processed_files"].append(file_result)
                
                if file_result["status"] == "success":
                    results["successful_files"] += 1
                    results["total_chunks"] += file_result["total_chunks"]
                    results["total_indexed_chunks"] += file_result["indexed_chunks"]
                else:
                    results["failed_files"] += 1
                
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                results["failed_files"] += 1
                results["processed_files"].append({
                    "status": "error",
                    "file_path": file_path,
                    "error": str(e)
                })
        
        logger.info(f"Bulk indexing completed: {results['successful_files']}/{results['total_files']} files processed successfully")
        return results
    
    def semantic_search(self, query: str, size: int = 10, include_similarity: bool = True) -> Dict[str, Any]:
        """
        Perform semantic search using embeddings.
        
        Args:
            query: Search query
            size: Number of results to return
            include_similarity: Whether to calculate similarity scores
            
        Returns:
            Search results with similarity scores
        """
        logger.info(f"Performing semantic search for query: '{query}'")
        
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Perform vector search in OpenSearch
            search_body = {
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": query_embedding}
                        }
                    }
                },
                "size": size
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            # Process results
            results = []
            for hit in response["hits"]["hits"]:
                result = {
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
                
                # Calculate similarity if requested
                if include_similarity and hit["_source"].get("embedding"):
                    similarity = self.embedding_service.calculate_similarity(
                        query_embedding, 
                        hit["_source"]["embedding"]
                    )
                    result["similarity"] = similarity
                
                results.append(result)
            
            return {
                "status": "success",
                "query": query,
                "total_results": response["hits"]["total"]["value"],
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e)
            }
    
    def hybrid_search(self, query: str, size: int = 10) -> Dict[str, Any]:
        """
        Perform hybrid search combining text and vector search.
        
        Args:
            query: Search query
            size: Number of results to return
            
        Returns:
            Combined search results
        """
        logger.info(f"Performing hybrid search for query: '{query}'")
        
        try:
            # Get text search results
            text_results = self.opensearch_service.search_documents(query, size)
            
            # Get semantic search results
            semantic_results = self.semantic_search(query, size)
            
            # Combine and deduplicate results
            combined_results = []
            seen_ids = set()
            
            # Add semantic results first (they tend to be more relevant)
            if semantic_results["status"] == "success":
                for result in semantic_results["results"]:
                    if result["id"] not in seen_ids:
                        result["search_type"] = "semantic"
                        combined_results.append(result)
                        seen_ids.add(result["id"])
            
            # Add text results
            for hit in text_results["hits"]["hits"]:
                if hit["_id"] not in seen_ids:
                    result = {
                        "id": hit["_id"],
                        "score": hit["_score"],
                        "content": hit["_source"].get("content", ""),
                        "metadata": {
                            "document_type": hit["_source"].get("document_type"),
                            "partner_name": hit["_source"].get("partner_name"),
                            "title": hit["_source"].get("title"),
                            "chunk_number": hit["_source"].get("chunk_number")
                        },
                        "search_type": "text"
                    }
                    combined_results.append(result)
                    seen_ids.add(hit["_id"])
            
            # Limit to requested size
            combined_results = combined_results[:size]
            
            return {
                "status": "success",
                "query": query,
                "total_results": len(combined_results),
                "results": combined_results
            }
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e)
            }
    
    def get_indexing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about indexed documents.
        
        Returns:
            Indexing statistics
        """
        try:
            # Get basic stats from OpenSearch
            doc_count = self.opensearch_service.get_document_count()
            health = self.opensearch_service.health_check()
            
            # Get additional stats by querying for unique documents
            search_body = {
                "size": 0,
                "aggs": {
                    "document_types": {
                        "terms": {"field": "document_type", "size": 10}
                    },
                    "partners": {
                        "terms": {"field": "partner_name", "size": 10}
                    },
                    "unique_chunks": {
                        "terms": {"field": "chunk_id", "size": 1000}
                    }
                }
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            return {
                "status": "success",
                "total_chunks": doc_count,
                "unique_documents": len(response["aggregations"]["unique_chunks"]["buckets"]),
                "document_types": [
                    {"type": bucket["key"], "count": bucket["doc_count"]}
                    for bucket in response["aggregations"]["document_types"]["buckets"]
                ],
                "partners": [
                    {"partner": bucket["key"], "count": bucket["doc_count"]}
                    for bucket in response["aggregations"]["partners"]["buckets"]
                ],
                "cluster_health": health.get("status", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Failed to get indexing stats: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """Generate metadata based on filename patterns."""
        filename_lower = filename.lower()
        
        if 'contract' in filename_lower:
            return {
                "document_type": "contract",
                "title": "Partnership Agreement"
            }
        elif 'payout' in filename_lower:
            return {
                "document_type": "payout_report",
                "title": "Payout Statement"
            }
        elif 'agreement' in filename_lower:
            return {
                "document_type": "agreement",
                "title": "Legal Agreement"
            }
        else:
            return {
                "document_type": "general",
                "title": filename
            }


# Utility function to index sample documents
def index_sample_documents() -> Dict[str, Any]:
    """Index all sample documents."""
    indexing_service = DocumentIndexingService()
    
    # Ensure index exists
    indexing_service.opensearch_service.create_index()
    
    # Index sample directory
    sample_dir = "data/sample_contracts"
    return indexing_service.index_directory(sample_dir)
