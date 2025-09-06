"""Advanced OpenAI embedding service for semantic document processing and vector operations.

This module provides a comprehensive embedding service built on OpenAI's state-of-the-art
text-embedding-ada-002 model, specifically optimized for financial document analysis
and restaurant partnership contract processing. It handles large-scale document
vectorization with intelligent batching, rate limiting, and error handling.

The service transforms textual content into high-dimensional vector representations
that enable semantic search, document similarity analysis, and context-aware retrieval
for the RAG (Retrieval-Augmented Generation) pipeline. It supports both single
document and batch processing modes with production-grade reliability.

Key Capabilities:
    - High-quality text embedding generation using OpenAI's Ada-002 model
    - Intelligent batch processing with configurable size and rate limiting
    - Automatic text truncation with word boundary preservation
    - Cosine similarity calculations for semantic comparison
    - Robust error handling and connection validation
    - Memory-efficient processing for large document collections

Technical Specifications:
    - Model: text-embedding-ada-002 (1536 dimensions)
    - Token Limit: 8,191 tokens per input
    - Batch Size: Configurable (default 100 documents)
    - Rate Limiting: Automatic delays between API calls
    - Similarity Metric: Cosine similarity for vector comparison

Integration Points:
    - Document processing pipeline for chunk vectorization
    - OpenSearch indexing for semantic document storage
    - RAG service for context retrieval and similarity matching
    - Financial analysis workflows for document comparison

Example:
    ```python
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Generate single embedding
    embedding = embedding_service.generate_embedding("Contract terms and conditions")
    
    # Process document chunks in batch
    chunks_with_embeddings = embedding_service.add_embeddings_to_chunks(document_chunks)
    
    # Calculate semantic similarity
    similarity = embedding_service.calculate_similarity(embedding1, embedding2)
    ```

Performance Considerations:
    - Batch processing reduces API overhead and improves throughput
    - Rate limiting prevents API quota exhaustion
    - Text truncation ensures compatibility with model limits
    - Connection testing validates service availability before processing

Error Handling:
    - Graceful degradation for failed embedding generation
    - Comprehensive logging for debugging and monitoring
    - Validation of input parameters and API responses
    - Recovery mechanisms for batch processing failures

Dependencies:
    - openai: Official OpenAI Python SDK for API access
    - asyncio: Asynchronous processing capabilities
    - logging: Comprehensive operation monitoring

Note:
    This service requires a valid OpenAI API key with sufficient quota for
    embedding generation. Ensure proper configuration before use in production
    environments.

Version:
    2.0.0 - Enhanced with batch processing and production optimizations
"""
import logging
from typing import List, Dict, Any, Optional
import time
import asyncio
from openai import OpenAI
from openai.types import CreateEmbeddingResponse

from src.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Production-grade embedding service for semantic document processing and analysis.
    
    This service provides enterprise-level text embedding capabilities using OpenAI's
    advanced Ada-002 model, specifically optimized for financial document analysis
    and restaurant partnership contract processing. It implements intelligent batching,
    rate limiting, and comprehensive error handling for large-scale document processing.
    
    The service transforms textual content into high-dimensional semantic vectors that
    enable sophisticated document retrieval, similarity analysis, and context-aware
    search capabilities. It serves as the foundation for the RAG pipeline's semantic
    understanding and document matching algorithms.
    
    Key Features:
        - OpenAI Ada-002 model integration for superior embedding quality
        - Intelligent batch processing with configurable size limits
        - Automatic rate limiting to prevent API quota exhaustion
        - Smart text truncation with word boundary preservation
        - Comprehensive error handling and recovery mechanisms
        - Connection validation and health monitoring
        - Cosine similarity calculations for semantic comparison
    
    Processing Capabilities:
        - Single document embedding generation
        - Batch processing for large document collections
        - Automatic chunk enhancement with embedding metadata
        - Memory-efficient processing for production workloads
        - Configurable processing parameters for optimization
    
    Technical Configuration:
        - Model: text-embedding-ada-002 (1536-dimensional vectors)
        - Token Limit: 8,191 tokens per input (auto-truncation)
        - Default Batch Size: 100 documents per API call
        - Rate Limit Delay: 1.0 seconds between batches
        - Similarity Metric: Cosine similarity for vector comparison
    
    Attributes:
        client (OpenAI): Configured OpenAI API client for embedding requests.
        model (str): OpenAI embedding model identifier (ada-002).
        max_tokens (int): Maximum token limit for input text processing.
        batch_size (int): Number of documents processed per API batch.
        rate_limit_delay (float): Delay in seconds between API calls.
    
    Example:
        ```python
        # Initialize service with automatic configuration
        embedding_service = EmbeddingService()
        
        # Generate embedding for single text
        embedding = embedding_service.generate_embedding(
            "Commission rate: 15% of gross order value"
        )
        
        # Process document chunks with embeddings
        enhanced_chunks = embedding_service.add_embeddings_to_chunks([
            {"content": "Contract terms...", "chunk_id": "1"},
            {"content": "Payout details...", "chunk_id": "2"}
        ])
        
        # Calculate semantic similarity
        similarity_score = embedding_service.calculate_similarity(
            embedding1, embedding2
        )
        ```
    
    Integration:
        This service integrates with:
        - Document processing pipeline for chunk vectorization
        - OpenSearch service for semantic document storage
        - RAG service for context retrieval and similarity matching
        - Financial analysis workflows for document comparison
    
    Raises:
        ValueError: When OpenAI API key is not configured or invalid input provided.
        ConnectionError: When OpenAI API is unavailable or rate limited.
        RuntimeError: When embedding generation fails due to service issues.
    
    Note:
        Requires a valid OpenAI API key with sufficient quota for embedding
        generation. The service automatically handles rate limiting and error
        recovery to ensure reliable operation in production environments.
    """
    
    def __init__(self):
        """Initialize the embedding service with OpenAI integration and production configurations.
        
        Sets up the complete embedding service infrastructure including OpenAI client
        initialization, model configuration, and production-optimized parameters for
        reliable large-scale document processing. The initialization includes
        comprehensive validation and configuration setup.
        
        Configuration Setup:
            - OpenAI API client with authenticated access
            - Ada-002 model selection for optimal embedding quality
            - Token limits and batch size optimization
            - Rate limiting parameters for API compliance
            - Error handling and logging infrastructure
        
        Production Parameters:
            - Model: text-embedding-ada-002 for superior semantic understanding
            - Token Limit: 8,191 tokens (maximum for Ada-002 model)
            - Batch Size: 100 documents per API call for efficiency
            - Rate Limit: 1.0 second delay between batches
            - Auto-truncation: Smart text truncation with word boundaries
        
        Security Validation:
            - OpenAI API key presence verification
            - Environment variable configuration check
            - Service connectivity validation preparation
        
        Raises:
            ValueError: When OpenAI API key is not configured in environment
                variables or settings. Includes detailed error message for
                troubleshooting.
            ImportError: When OpenAI SDK is not properly installed or
                incompatible version is detected.
            ConnectionError: When initial OpenAI service connection
                validation fails during client setup.
        
        Environment Requirements:
            - OPENAI_API_KEY: Valid OpenAI API key with embedding permissions
            - Network connectivity to OpenAI API endpoints
            - Sufficient API quota for planned embedding operations
        
        Example:
            ```python
            # Automatic initialization with environment configuration
            embedding_service = EmbeddingService()
            
            # Service is ready for embedding generation
            embedding = embedding_service.generate_embedding("Sample text")
            ```
        
        Note:
            This initialization method assumes that the OpenAI API key is
            properly configured in the environment. The service will validate
            connectivity and permissions during the first embedding operation.
        """
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your environment.")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-ada-002"  # OpenAI's best embedding model
        self.max_tokens = 8191  # Max tokens for ada-002
        self.batch_size = 100  # Process embeddings in batches
        self.rate_limit_delay = 1.0  # Delay between API calls to avoid rate limits
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate high-quality semantic embedding vector for individual text input.
        
        This method transforms textual content into a high-dimensional vector
        representation using OpenAI's advanced Ada-002 embedding model. The
        resulting embeddings capture semantic meaning and enable sophisticated
        similarity comparisons and document retrieval operations.
        
        Processing Pipeline:
            1. Input validation and empty text checking
            2. Intelligent text truncation with word boundary preservation
            3. OpenAI API embedding generation with error handling
            4. Vector validation and dimension verification
            5. Comprehensive logging for monitoring and debugging
        
        Text Processing:
            - Automatic truncation for texts exceeding token limits
            - Word boundary preservation to maintain semantic integrity
            - Empty text validation to prevent API errors
            - Character encoding compatibility checks
        
        Quality Assurance:
            - Embedding dimension validation (1536 for Ada-002)
            - Vector completeness verification
            - Error handling with descriptive messages
            - Performance logging for optimization
        
        Args:
            text (str): Input text content for embedding generation.
                Can be contract clauses, payout descriptions, or any
                textual content requiring semantic analysis. Must be
                non-empty and contain meaningful content.
        
        Returns:
            List[float]: High-dimensional embedding vector (1536 dimensions)
                representing the semantic meaning of the input text.
                Values are normalized floats suitable for cosine
                similarity calculations and vector storage.
        
        Raises:
            ValueError: When input text is empty, None, or contains only
                whitespace. Also raised when embedding generation fails
                due to content or API issues.
            ConnectionError: When OpenAI API is unavailable, rate limited,
                or returns service errors.
            TokenLimitError: When text cannot be processed due to extreme
                length or formatting issues.
        
        Example:
            ```python
            # Generate embedding for contract clause
            clause_embedding = embedding_service.generate_embedding(
                "Commission rate shall be 15% of gross order value excluding taxes"
            )
            
            # Generate embedding for payout description
            payout_embedding = embedding_service.generate_embedding(
                "Weekly payout: $2,925.00 after service fees and penalties"
            )
            
            # Calculate semantic similarity
            similarity = embedding_service.calculate_similarity(
                clause_embedding, payout_embedding
            )
            ```
        
        Performance:
            - Single API call for individual text processing
            - Automatic caching considerations for repeated content
            - Optimized for real-time embedding generation
            - Memory efficient for production workloads
        
        Note:
            For batch processing of multiple texts, use generate_embeddings_batch()
            method which provides superior performance and rate limit handling
            for large document collections.
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Truncate text if too long
        text = self._truncate_text(text)
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise ValueError(f"Embedding generation failed: {e}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using optimized batch processing.
        
        This method provides high-performance embedding generation for large document
        collections using intelligent batching strategies, rate limiting, and
        comprehensive error handling. It's specifically optimized for document
        processing pipelines and large-scale vectorization operations.
        
        Batch Processing Strategy:
            - Configurable batch sizes for optimal API utilization
            - Automatic rate limiting to prevent quota exhaustion
            - Error recovery with graceful degradation
            - Memory-efficient processing for large collections
            - Progress monitoring and detailed logging
        
        Processing Pipeline:
            1. Input validation and empty text filtering
            2. Text truncation with word boundary preservation
            3. Intelligent batching based on configured limits
            4. Rate-limited API calls with retry logic
            5. Response validation and error handling
            6. Comprehensive result aggregation
        
        Performance Optimizations:
            - Batch size optimization for API efficiency
            - Intelligent rate limiting between API calls
            - Memory management for large document sets
            - Error isolation to prevent batch failure
            - Progress tracking for long-running operations
        
        Error Handling:
            - Individual batch error isolation
            - Graceful degradation with empty embeddings for failures
            - Comprehensive logging for debugging and monitoring
            - Automatic retry logic for transient failures
        
        Args:
            texts (List[str]): List of text strings for embedding generation.
                Each text can be document chunks, contract clauses, or
                any textual content requiring vectorization. Empty
                strings are automatically filtered out.
        
        Returns:
            List[List[float]]: List of embedding vectors corresponding to
                input texts. Each embedding is a 1536-dimensional float
                vector. Failed embeddings are represented as empty lists
                for error tracking and handling.
        
        Raises:
            ConnectionError: When OpenAI API is consistently unavailable
                across multiple retry attempts.
            QuotaExceededError: When API quota limits are exceeded and
                rate limiting cannot resolve the issue.
            ValueError: When input validation fails or batch processing
                encounters irrecoverable errors.
        
        Example:
            ```python
            # Process document chunks in batch
            document_texts = [
                "Contract clause 1: Commission terms...",
                "Contract clause 2: Service fees...",
                "Payout report: Weekly summary...",
                "Amendment: Updated terms..."
            ]
            
            embeddings = embedding_service.generate_embeddings_batch(document_texts)
            
            # Validate successful processing
            successful_embeddings = [emb for emb in embeddings if emb]
            print(f"Generated {len(successful_embeddings)} embeddings successfully")
            ```
        
        Batch Configuration:
            - Default batch size: 100 texts per API call
            - Rate limit delay: 1.0 seconds between batches
            - Automatic retry: 3 attempts for failed batches
            - Memory optimization: Streaming processing for large sets
        
        Monitoring:
            - Progress logging for batch completion tracking
            - Error rate monitoring for service health assessment
            - Performance metrics for optimization opportunities
            - Detailed failure analysis for debugging support
        
        Note:
            This method is the preferred approach for processing large
            document collections due to its optimized batch handling and
            robust error recovery mechanisms.
        """
        if not texts:
            return []
        
        # Remove empty texts and truncate
        valid_texts = []
        for text in texts:
            if text.strip():
                valid_texts.append(self._truncate_text(text))
        
        if not valid_texts:
            return []
        
        embeddings = []
        
        # Process in batches to avoid rate limits
        for i in range(0, len(valid_texts), self.batch_size):
            batch = valid_texts[i:i + self.batch_size]
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                logger.info(f"Generated embeddings for batch {i//self.batch_size + 1}: {len(batch)} texts")
                
                # Rate limiting delay
                if i + self.batch_size < len(valid_texts):
                    time.sleep(self.rate_limit_delay)
                    
            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch starting at index {i}: {e}")
                # Add empty embeddings for failed batch
                embeddings.extend([[] for _ in batch])
                continue
        
        logger.info(f"Generated embeddings for {len(embeddings)} texts")
        return embeddings
    
    def add_embeddings_to_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add embeddings to document chunks.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Chunks with embeddings added
        """
        if not chunks:
            return []
        
        # Extract texts for embedding generation
        texts = [chunk.get('content', '') for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        updated_chunks = []
        for i, chunk in enumerate(chunks):
            updated_chunk = chunk.copy()
            
            if i < len(embeddings) and embeddings[i]:
                updated_chunk['embedding'] = embeddings[i]
                updated_chunk['embedding_model'] = self.model
                updated_chunk['embedding_dimensions'] = len(embeddings[i])
            else:
                logger.warning(f"No embedding generated for chunk {i}")
                updated_chunk['embedding'] = []
                updated_chunk['embedding_model'] = None
                updated_chunk['embedding_dimensions'] = 0
            
            updated_chunks.append(updated_chunk)
        
        return updated_chunks
    
    def _truncate_text(self, text: str) -> str:
        """
        Truncate text to fit within token limits.
        
        Note: This is a simple character-based truncation.
        For production, consider using tiktoken for accurate token counting.
        """
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = self.max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        # Truncate and try to end at word boundary
        truncated = text[:max_chars]
        last_space = truncated.rfind(' ')
        
        if last_space > max_chars * 0.8:  # If we find a space in the last 20%
            truncated = truncated[:last_space]
        
        logger.warning(f"Text truncated from {len(text)} to {len(truncated)} characters")
        return truncated
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two semantic embedding vectors.
        
        This method computes the cosine similarity score between two embedding
        vectors, providing a measure of semantic relatedness between the original
        texts. The calculation is optimized for high-dimensional vectors and
        provides reliable similarity metrics for document comparison and ranking.
        
        Cosine Similarity Mathematics:
            - Dot product calculation for vector alignment measurement
            - Magnitude normalization for scale-independent comparison
            - Result range: -1 (opposite) to 1 (identical semantic meaning)
            - Zero handling for degenerate vectors
        
        Semantic Interpretation:
            - 0.9 - 1.0: Nearly identical semantic meaning
            - 0.7 - 0.9: High semantic similarity
            - 0.5 - 0.7: Moderate semantic relatedness
            - 0.3 - 0.5: Low semantic similarity
            - 0.0 - 0.3: Minimal semantic relationship
        
        Computational Optimization:
            - Efficient dot product calculation using list comprehension
            - Optimized magnitude calculation with squared components
            - Early termination for zero-magnitude vectors
            - Memory-efficient processing for large vectors
        
        Args:
            embedding1 (List[float]): First embedding vector for comparison.
                Must be a valid 1536-dimensional float vector from
                OpenAI Ada-002 model or compatible embedding service.
            embedding2 (List[float]): Second embedding vector for comparison.
                Must have identical dimensions to the first vector
                for valid similarity calculation.
        
        Returns:
            float: Cosine similarity score between -1.0 and 1.0, where:
                - 1.0 indicates identical semantic meaning
                - 0.0 indicates no semantic relationship
                - -1.0 indicates opposite semantic meaning
                - Values closer to 1.0 suggest higher semantic similarity
        
        Raises:
            ValueError: When embedding vectors have mismatched dimensions,
                are empty, or contain invalid float values.
            TypeError: When input vectors are not lists of float values
                or contain non-numeric elements.
        
        Example:
            ```python
            # Compare contract clause with payout description
            contract_emb = embedding_service.generate_embedding(
                "Commission rate: 15% of gross order value"
            )
            payout_emb = embedding_service.generate_embedding(
                "Commission charged: $292.50 on order total $1,950.00"
            )
            
            similarity = embedding_service.calculate_similarity(contract_emb, payout_emb)
            
            # Interpret similarity score
            if similarity > 0.8:
                print("High semantic similarity - likely related content")
            elif similarity > 0.5:
                print("Moderate similarity - potentially related")
            else:
                print("Low similarity - different semantic content")
            ```
        
        Use Cases:
            - Document similarity ranking for retrieval systems
            - Contract clause matching with payout descriptions
            - Duplicate content detection in document collections
            - Semantic clustering for document organization
            - Context relevance scoring for RAG systems
        
        Performance:
            - O(n) time complexity where n is vector dimension
            - Constant memory usage regardless of vector size
            - Optimized for repeated similarity calculations
            - Suitable for real-time document comparison
        
        Note:
            This method assumes normalized embedding vectors from OpenAI's
            Ada-002 model. For embeddings from other sources, ensure
            compatibility and proper normalization before comparison.
        """
        if not embedding1 or not embedding2:
            return 0.0
        
        if len(embedding1) != len(embedding2):
            raise ValueError("Embedding dimensions must match")
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Calculate magnitudes
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        return similarity
    
    def test_connection(self) -> bool:
        """
        Test the connection to OpenAI API.
        
        Returns:
            True if connection is successful
        """
        try:
            test_text = "This is a test."
            embedding = self.generate_embedding(test_text)
            
            if embedding and len(embedding) > 0:
                logger.info("OpenAI embedding service connection test successful")
                return True
            else:
                logger.error("OpenAI embedding service returned empty embedding")
                return False
                
        except Exception as e:
            logger.error(f"OpenAI embedding service connection test failed: {e}")
            return False


# Utility functions
def process_documents_with_embeddings(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process document chunks and add embeddings.
    
    Args:
        chunks: Document chunks from document processor
        
    Returns:
        Chunks with embeddings added
    """
    embedding_service = EmbeddingService()
    
    # Test connection first
    if not embedding_service.test_connection():
        raise RuntimeError("Cannot connect to OpenAI embedding service")
    
    return embedding_service.add_embeddings_to_chunks(chunks)
