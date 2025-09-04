"""
Document processing service for text extraction and chunking.
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
    """Service for processing documents and extracting text."""
    
    def __init__(self):
        """Initialize document processor."""
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
    
    def process_file(self, file_path: str, document_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process a file and return chunks with metadata.
        
        Args:
            file_path: Path to the file to process
            document_metadata: Additional metadata for the document
            
        Returns:
            List of document chunks with metadata
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
