"""OpenAI embedding service for document vectorization and semantic search.

Provides text embedding generation using OpenAI's Ada-002 model with batch processing,
rate limiting, and similarity calculations for financial document analysis.

Key Features:
    - Text-to-vector embedding generation
    - Batch processing with rate limiting
    - Cosine similarity calculations
    - Document chunk enhancement

Example:
    ```python
    service = EmbeddingService()
    embedding = service.generate_embedding("Contract terms")
    similarity = service.calculate_similarity(emb1, emb2)
    ```
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
    """OpenAI embedding service for document vectorization and semantic analysis.
    
    Generates text embeddings using Ada-002 model with batch processing, rate limiting,
    and similarity calculations for financial document analysis.
    
    Features:
        - Single and batch embedding generation
        - Automatic text truncation and rate limiting
        - Cosine similarity calculations
        - Document chunk enhancement
    
    Attributes:
        client: OpenAI API client
        model: Ada-002 embedding model
        max_tokens: Token limit (8,191)
        batch_size: Documents per batch (100)
        rate_limit_delay: Delay between batches (1.0s)
    """
    
    def __init__(self):
        """Initialize embedding service with OpenAI client and configuration.
        
        Sets up Ada-002 model, batch processing, and rate limiting parameters.
        
        Raises:
            ValueError: When OpenAI API key is not configured.
        """
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your environment.")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-ada-002"  # OpenAI's best embedding model
        self.max_tokens = 8191  # Max tokens for ada-002
        self.batch_size = 100  # Process embeddings in batches
        self.rate_limit_delay = 1.0  # Delay between API calls to avoid rate limits
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate semantic embedding vector for text using Ada-002 model.
        
        Transforms text into 1536-dimensional vector with automatic truncation
        and validation.
        
        Args:
            text: Input text content for embedding generation.
        
        Returns:
            1536-dimensional embedding vector as list of floats.
        
        Raises:
            ValueError: When text is empty or embedding generation fails.
            ConnectionError: When OpenAI API is unavailable.
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
        """Generate embeddings for multiple texts using batch processing.
        
        Args:
            texts (List[str]): List of text strings for embedding generation.
        
        Returns:
            List[List[float]]: List of 1536-dimensional embedding vectors.
                Failed embeddings are represented as empty lists.
        
        Raises:
            ConnectionError: When OpenAI API is unavailable.
            ValueError: When input validation fails.
        
        Example:
            ```python
            texts = ["Contract clause...", "Payout report..."]
            embeddings = service.generate_embeddings_batch(texts)
            ```
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
        """Calculate cosine similarity between two embedding vectors.
        
        Args:
            embedding1 (List[float]): First embedding vector.
            embedding2 (List[float]): Second embedding vector.
        
        Returns:
            float: Cosine similarity score between -1.0 and 1.0, where
                1.0 indicates identical meaning and 0.0 indicates no relationship.
        
        Raises:
            ValueError: When embedding dimensions don't match.
        
        Example:
            ```python
            similarity = service.calculate_similarity(emb1, emb2)
            ```
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
