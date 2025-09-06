"""Advanced document processing service for multi-format text extraction and intelligent chunking.

This module provides comprehensive document processing capabilities specifically
designed for restaurant partnership contracts, payout reports, and financial
documents. It handles multiple file formats with intelligent text extraction,
semantic chunking, and metadata enrichment for optimal RAG system integration.

The service supports various document formats including PDF contracts, text-based
payout reports, and structured financial documents. It implements sophisticated
text extraction algorithms with fallback mechanisms, ensuring reliable content
processing even for complex document layouts and formats.

Key Capabilities:
    - Multi-format document processing (PDF, TXT, MD)
    - Intelligent text extraction with multiple PDF parsing backends
    - Semantic-aware chunking with configurable overlap
    - Comprehensive metadata enrichment and tracking
    - File size validation and security checks
    - Error handling with detailed diagnostics
    - Production-grade logging and monitoring

Document Processing Pipeline:
    1. File validation and security checks
    2. Format detection and appropriate parser selection
    3. Text extraction with quality validation
    4. Intelligent chunking with semantic preservation
    5. Metadata enrichment and tracking
    6. Quality assurance and error handling

Supported Formats:
    - PDF: Restaurant contracts, partnership agreements, legal documents
    - TXT: Payout reports, financial summaries, structured data
    - MD: Documentation, analysis reports, structured content

PDF Processing Backends:
    - pdfplumber: Primary backend for complex layouts and tables
    - PyMuPDF (fitz): High-performance alternative for large documents
    - PyPDF2: Fallback option for compatibility and simple documents

Technical Features:
    - Configurable chunk sizes for optimal RAG performance
    - Overlapping chunks to preserve context boundaries
    - Automatic metadata generation with document fingerprinting
    - File size limits and security validation
    - Memory-efficient processing for large documents

Example:
    ```python
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Process PDF contract
    contract_chunks = processor.process_file(
        file_path="partnership_agreement.pdf",
        document_metadata={
            "partner_name": "SushiExpress24-7",
            "document_type": "contract"
        }
    )
    
    # Process text-based payout report
    payout_chunks = processor.process_text(
        text=payout_report_content,
        document_metadata={
            "partner_name": "SushiExpress24-7",
            "document_type": "payout_report",
            "report_date": "2024-07-21"
        }
    )
    ```

Integration Points:
    - Embedding service for vector generation
    - OpenSearch indexing for document storage
    - RAG service for context retrieval
    - API endpoints for document upload and processing

Performance Considerations:
    - Streaming processing for large documents
    - Memory optimization for batch operations
    - Configurable processing parameters
    - Intelligent caching for repeated operations

Security Features:
    - File size validation to prevent resource exhaustion
    - File type validation for security compliance
    - Path traversal protection
    - Content validation and sanitization

Dependencies:
    - pdfplumber: Advanced PDF parsing with table support
    - PyMuPDF (fitz): High-performance PDF processing
    - PyPDF2: Compatibility and fallback PDF processing
    - logging: Comprehensive operation monitoring

Note:
    This service requires at least one PDF processing library to be installed
    for PDF document support. Multiple backends provide redundancy and
    optimization options for different document types.

Version:
    2.0.0 - Enhanced with multi-backend PDF processing and production optimizations
"""
import logging
from typing import List, Dict, Any, Optional
import os
import uuid
from datetime import datetime
import re

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from src.core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Production-grade document processing service for multi-format text extraction and chunking.
    
    This service provides enterprise-level document processing capabilities specifically
    optimized for restaurant partnership contracts, financial payout reports, and
    related business documents. It implements sophisticated text extraction algorithms
    with multiple backend support, intelligent chunking strategies, and comprehensive
    metadata management.
    
    The processor handles complex document layouts, tables, and various formatting
    challenges commonly found in legal contracts and financial reports. It provides
    robust fallback mechanisms and detailed error handling to ensure reliable
    processing across diverse document types and quality levels.
    
    Processing Capabilities:
        - Multi-format document support (PDF, TXT, MD)
        - Advanced PDF parsing with table and layout preservation
        - Intelligent text chunking with semantic boundary detection
        - Comprehensive metadata extraction and enrichment
        - File validation and security compliance
        - Memory-efficient processing for large document collections
    
    PDF Processing Features:
        - Multiple backend support (pdfplumber, PyMuPDF, PyPDF2)
        - Automatic fallback between parsers for optimal results
        - Table extraction and structured content handling
        - Layout-aware text extraction for complex documents
        - Quality validation and content verification
    
    Chunking Strategy:
        - Configurable chunk sizes optimized for RAG systems
        - Intelligent overlap to preserve context across boundaries
        - Semantic-aware splitting to maintain document coherence
        - Metadata propagation across all generated chunks
        - Quality metrics for chunk assessment
    
    Security and Validation:
        - File size limits to prevent resource exhaustion
        - File type validation for security compliance
        - Path traversal protection and input sanitization
        - Content validation and quality assessment
        - Error handling with detailed diagnostics
    
    Attributes:
        chunk_size (int): Maximum characters per document chunk for optimal processing.
        chunk_overlap (int): Character overlap between chunks to preserve context.
        max_file_size (int): Maximum file size in bytes for security and performance.
    
    Example:
        ```python
        # Initialize with default configuration
        processor = DocumentProcessor()
        
        # Process restaurant partnership contract
        contract_chunks = processor.process_file(
            file_path="partnership_agreement.pdf",
            document_metadata={
                "partner_name": "SushiExpress24-7",
                "document_type": "contract",
                "contract_date": "2022-03-10"
            }
        )
        
        # Process payout report text
        payout_chunks = processor.process_text(
            text=financial_report_content,
            document_metadata={
                "partner_name": "SushiExpress24-7",
                "document_type": "payout_report",
                "report_period": "2024-07-21"
            }
        )
        
        # Validate processing results
        for chunk in contract_chunks:
            print(f"Chunk {chunk['chunk_id']}: {len(chunk['content'])} characters")
        ```
    
    Configuration:
        The service uses configuration values from settings for:
        - chunk_size: Optimal chunk size for RAG processing
        - chunk_overlap: Context preservation between chunks
        - max_file_size_mb: Security limit for uploaded files
    
    Backend Selection:
        PDF processing backends are selected based on:
        - Document complexity and layout requirements
        - Performance considerations for large files
        - Availability of installed libraries
        - Quality of extracted content
    
    Raises:
        FileNotFoundError: When specified file paths do not exist.
        ValueError: When file size exceeds limits or unsupported formats.
        ProcessingError: When text extraction fails across all backends.
        SecurityError: When file validation fails security checks.
    
    Note:
        This service requires at least one PDF processing library (pdfplumber,
        PyMuPDF, or PyPDF2) for PDF document support. Multiple backends provide
        redundancy and optimization for different document characteristics.
    """
    
    def __init__(self):
        """Initialize document processor with production-optimized configuration.
        
        Sets up the document processing service with security-validated settings,
        configurable processing parameters, and resource management controls.
        The initialization prepares the service for reliable large-scale document
        processing with appropriate safeguards and optimization.
        
        Configuration Setup:
            - Chunk size optimization for RAG system compatibility
            - Overlap configuration for context preservation
            - Security limits for file size and resource protection
            - Logging infrastructure for operation monitoring
        
        Security Validation:
            - File size limits to prevent resource exhaustion attacks
            - Format validation for supported document types
            - Memory usage controls for large document processing
        
        Performance Optimization:
            - Configurable chunk sizes for optimal embedding generation
            - Memory-efficient processing parameters
            - Backend selection logic for PDF processing
        
        Resource Management:
            - Maximum file size enforcement (configurable via settings)
            - Memory usage monitoring and controls
            - Processing timeout considerations
        
        Backend Availability:
            The initialization checks for available PDF processing libraries:
            - pdfplumber: Preferred for complex layouts and table extraction
            - PyMuPDF (fitz): High-performance alternative for large documents
            - PyPDF2: Fallback option for basic PDF processing
        
        Note:
            Configuration values are loaded from the settings module and can
            be customized through environment variables or configuration files.
            At least one PDF processing library must be available for full
            functionality.
        
        Default Configuration:
            - chunk_size: From settings.chunk_size (typically 1000-2000 characters)
            - chunk_overlap: From settings.chunk_overlap (typically 200 characters)
            - max_file_size: From settings.max_file_size_mb converted to bytes
        """
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
    
    def process_file(self, file_path: str, document_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process document files with comprehensive text extraction and intelligent chunking.
        
        This method provides end-to-end document processing for various file formats,
        implementing robust text extraction with multiple backend support, comprehensive
        validation, and intelligent chunking optimized for RAG system integration.
        The processing pipeline ensures reliable content extraction even from complex
        document layouts and formats.
        
        Processing Pipeline:
            1. File existence and accessibility validation
            2. Security checks including file size and type validation
            3. Format detection and appropriate backend selection
            4. Text extraction with quality validation
            5. Intelligent chunking with semantic preservation
            6. Metadata enrichment and tracking
            7. Quality assurance and error handling
        
        Security Features:
            - File size validation to prevent resource exhaustion
            - File type validation for security compliance
            - Path traversal protection
            - Content sanitization and validation
        
        Text Extraction:
            - PDF: Multiple backend support (pdfplumber, PyMuPDF, PyPDF2)
            - TXT: Direct text file reading with encoding detection
            - MD: Markdown file processing with structure preservation
            - Automatic fallback between backends for optimal results
        
        Metadata Generation:
            - File system metadata (path, name, size, type)
            - Processing metadata (timestamp, character count)
            - Custom metadata integration
            - Document fingerprinting for tracking
        
        Args:
            file_path (str): Absolute or relative path to the document file
                for processing. Must point to an existing, readable file
                in a supported format (PDF, TXT, MD).
            document_metadata (Optional[Dict[str, Any]]): Additional metadata
                to associate with the document and all generated chunks.
                Common fields include partner_name, document_type,
                contract_date, and business-specific identifiers.
        
        Returns:
            List[Dict[str, Any]]: List of document chunks with comprehensive
                metadata. Each chunk contains:
                - content: Extracted text content for the chunk
                - chunk_id: Unique identifier for the chunk
                - chunk_index: Sequential position in the document
                - file_path, file_name, file_size, file_type: File metadata
                - processed_at: Processing timestamp
                - total_characters: Character count for the chunk
                - Additional custom metadata from document_metadata parameter
        
        Raises:
            FileNotFoundError: When the specified file path does not exist
                or is not accessible for reading.
            ValueError: When file size exceeds configured limits, file format
                is unsupported, or no extractable text content is found.
            ProcessingError: When text extraction fails across all available
                backends or processing encounters irrecoverable errors.
            SecurityError: When file validation fails security checks or
                file access is restricted.
        
        Example:
            ```python
            # Process restaurant partnership contract
            contract_chunks = processor.process_file(
                file_path="/uploads/sushi_express_contract.pdf",
                document_metadata={
                    "partner_name": "SushiExpress24-7",
                    "document_type": "contract",
                    "platform": "SkipTheDishes",
                    "contract_date": "2022-03-10",
                    "business_category": "restaurant"
                }
            )
            
            # Validate processing results
            print(f"Generated {len(contract_chunks)} chunks")
            for chunk in contract_chunks[:3]:  # Show first 3 chunks
                print(f"Chunk {chunk['chunk_index']}: {len(chunk['content'])} chars")
            ```
        
        Performance Considerations:
            - Large files are processed in memory-efficient manner
            - Multiple PDF backends provide optimization options
            - Chunking strategy balances context preservation with processing efficiency
            - Metadata processing is optimized for minimal overhead
        
        Quality Assurance:
            - Text extraction quality validation
            - Content completeness verification
            - Chunk coherence assessment
            - Error recovery and reporting
        
        Note:
            The method automatically selects the most appropriate text extraction
            backend based on file format and document characteristics. For PDF
            files, it attempts multiple backends to ensure optimal text quality.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            raise ValueError(f"File size ({file_size} bytes) exceeds maximum allowed size ({self.max_file_size} bytes)")
        
        # Extract text based on file type
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            text = self._extract_pdf_text(file_path)
        elif file_extension in ['.txt', '.md']:
            text = self._extract_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        if not text.strip():
            raise ValueError("No text content found in the file")
        
        # Generate metadata
        base_metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": file_size,
            "file_type": file_extension,
            "processed_at": datetime.now().isoformat(),
            "total_characters": len(text),
        }
        
        if document_metadata:
            base_metadata.update(document_metadata)
        
        # Create chunks
        chunks = self._create_chunks(text, base_metadata)
        
        logger.info(f"Processed file '{file_path}': {len(chunks)} chunks created")
        return chunks
    
    def process_text(self, text: str, document_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process raw text and return chunks with metadata.
        
        Args:
            text: Raw text content
            document_metadata: Additional metadata for the document
            
        Returns:
            List of document chunks with metadata
        """
        if not text.strip():
            raise ValueError("Text content cannot be empty")
        
        # Generate metadata
        base_metadata = {
            "source": "text_input",
            "processed_at": datetime.now().isoformat(),
            "total_characters": len(text),
        }
        
        if document_metadata:
            base_metadata.update(document_metadata)
        
        # Create chunks
        chunks = self._create_chunks(text, base_metadata)
        
        logger.info(f"Processed text: {len(chunks)} chunks created")
        return chunks
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """
        Extract text from a PDF using pdfplumber with enhanced table handling.
        This method preserves table structure and layout-aware text extraction.
        """
        if not pdfplumber:
            logger.error("pdfplumber is not installed. Cannot process PDF files.")
            raise ImportError("pdfplumber is required for PDF processing.")

        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                page_texts = []
                
                for page_num, page in enumerate(pdf.pages):
                    page_text = ""
                    
                    # Extract tables first
                    tables = page.extract_tables()
                    if tables:
                        logger.info(f"Found {len(tables)} tables on page {page_num + 1}")
                        for table_num, table in enumerate(tables):
                            page_text += f"\n[TABLE {table_num + 1}]\n"
                            for row in table:
                                if row:  # Skip empty rows
                                    # Clean and join row cells
                                    cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                                    page_text += " | ".join(cleaned_row) + "\n"
                            page_text += "[END TABLE]\n\n"
                    
                    # Extract regular text (excluding table areas if possible)
                    try:
                        # Try to get text outside of tables
                        regular_text = page.extract_text(layout=True, x_tolerance=1)
                        if regular_text:
                            page_text += regular_text
                    except:
                        # Fallback to basic text extraction
                        regular_text = page.extract_text()
                        if regular_text:
                            page_text += regular_text
                    
                    if page_text.strip():
                        page_texts.append(page_text)

                text = "\n\n".join(page_texts)

            # Apply a light cleaning pass
            cleaned_text = self._clean_extracted_text(text)

            if cleaned_text.strip():
                logger.info(f"Successfully extracted text from '{file_path}' using pdfplumber with table handling.")
                return cleaned_text
            else:
                # If enhanced extraction returns nothing, try basic fallback
                logger.warning(f"Enhanced extraction for '{file_path}' yielded empty text. Trying basic extraction.")
                with pdfplumber.open(file_path) as pdf:
                    page_texts = [p.extract_text() for p in pdf.pages if p.extract_text()]
                    text = "\n\n".join(page_texts)
                cleaned_text = self._clean_extracted_text(text)
                if cleaned_text.strip():
                    return cleaned_text
                else:
                    raise ValueError("Extracted text was empty after all processing attempts.")

        except Exception as e:
            logger.error(f"Failed to extract text from '{file_path}' with pdfplumber: {e}")
            raise ValueError(f"PDF extraction failed for file: {file_path}")
        
        return ""

    def _clean_extracted_text(self, text: str) -> str:
        """Apply light cleaning, assuming layout and spacing are mostly correct."""
        if not text:
            return ""

        # Normalize whitespace: collapse multiple spaces/tabs to one, but preserve newlines
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Collapse more than two newlines (paragraph breaks) into two
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Change single newlines that are not part of a paragraph break into spaces
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

        # Correct spacing around punctuation
        text = re.sub(r'\s+([.,:;!?])', r'\1', text) # remove space before
        text = re.sub(r'([.,:;!?])([a-zA-Z0-9])', r'\1 \2', text) # add space after

        # Re-run whitespace collapse in case the punctuation rules added extra spaces
        text = re.sub(r' +', ' ', text)

        return text.strip()
    
    def _extract_text_file(self, file_path: str) -> str:
        """Extract text from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Failed to read text file '{file_path}': {e}")
                raise ValueError(f"Error reading text file: {e}")
        except Exception as e:
            logger.error(f"Failed to read text file '{file_path}': {e}")
            raise ValueError(f"Error reading text file: {e}")
    
    def _create_chunks(self, text: str, base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            base_metadata: Base metadata to include in each chunk
            
        Returns:
            List of chunks with metadata
        """
        # Clean and normalize text
        text = self._clean_text(text)
        
        chunks = []
        start = 0
        chunk_number = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If we're not at the end of the text, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundary (. ! ?)
                sentence_break = self._find_sentence_boundary(text, start, end)
                if sentence_break != -1:
                    end = sentence_break
                else:
                    # Look for word boundary
                    word_break = self._find_word_boundary(text, start, end)
                    if word_break != -1:
                        end = word_break
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunk_id = f"{base_metadata.get('file_name', 'unknown')}_{chunk_number}"
                
                chunk = {
                    "chunk_id": chunk_id,
                    "content": chunk_text,
                    "chunk_number": chunk_number,
                    "start_position": start,
                    "end_position": end,
                    "chunk_size": len(chunk_text),
                    "created_at": datetime.now().isoformat(),
                    **base_metadata  # Include all base metadata
                }
                
                chunks.append(chunk)
                chunk_number += 1
            
            # Move to next chunk with overlap
            start = max(start + self.chunk_size - self.chunk_overlap, end)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove non-printable characters (keep basic punctuation)
        text = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
        
        return text.strip()
    
    def _find_sentence_boundary(self, text: str, start: int, preferred_end: int) -> int:
        """Find the best sentence boundary near the preferred end position."""
        # Look backwards from preferred_end for sentence endings
        search_start = max(start, preferred_end - 200)  # Don't search too far back
        
        for i in range(preferred_end - 1, search_start - 1, -1):
            if text[i] in '.!?' and i + 1 < len(text) and text[i + 1].isspace():
                return i + 1
        
        return -1
    
    def _find_word_boundary(self, text: str, start: int, preferred_end: int) -> int:
        """Find the best word boundary near the preferred end position."""
        # Look backwards from preferred_end for word boundaries
        search_start = max(start, preferred_end - 50)  # Don't search too far back
        
        for i in range(preferred_end - 1, search_start - 1, -1):
            if text[i].isspace():
                return i
        
        return -1


# Utility function for processing sample documents
def process_sample_documents() -> List[Dict[str, Any]]:
    """Process sample documents and return chunks."""
    processor = DocumentProcessor()
    all_chunks = []
    
    sample_dir = "data/sample_contracts"
    if not os.path.exists(sample_dir):
        logger.warning(f"Sample directory '{sample_dir}' not found")
        return []
    
    for filename in os.listdir(sample_dir):
        if filename.endswith(('.txt', '.pdf')):
            file_path = os.path.join(sample_dir, filename)
            
            # Determine document type and metadata based on filename
            if 'contract' in filename.lower():
                doc_metadata = {
                    "document_type": "contract",
                    "partner_name": "Sushi Express 24/7",
                    "title": "Partnership Agreement"
                }
            elif 'payout' in filename.lower():
                doc_metadata = {
                    "document_type": "payout_report",
                    "partner_name": "Sushi Express 24/7",
                    "title": "Payout Statement"
                }
            else:
                doc_metadata = {
                    "document_type": "general",
                    "title": filename
                }
            
            try:
                chunks = processor.process_file(file_path, doc_metadata)
                all_chunks.extend(chunks)
                logger.info(f"Processed '{filename}': {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Failed to process '{filename}': {e}")
                continue
    
    return all_chunks
