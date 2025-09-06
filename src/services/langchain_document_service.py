"""LangChain-integrated document processing for RAG applications.

Provides document processing using LangChain's RecursiveCharacterTextSplitter,
optimized for financial contracts and restaurant partnership documents.

Key Features:
    - LangChain Document object creation for RAG integration
    - Semantic boundary preservation with recursive splitting
    - Multi-format support with unified output format
    - Comprehensive metadata management

Example:
    ```python
    processor = LangChainDocumentProcessor()
    documents = processor.process_file("contract.pdf", {"partner": "Restaurant"})
    ```
"""
import logging
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from src.services.document_service import DocumentProcessor
from src.core.config import settings

logger = logging.getLogger(__name__)


class LangChainDocumentProcessor:
    """LangChain document processor for RAG pipeline integration.
    
    Processes documents using RecursiveCharacterTextSplitter optimized for 
    financial contracts and restaurant partnership documents.
    
    Attributes:
        base_processor (DocumentProcessor): Core text extraction service.
        text_splitter (RecursiveCharacterTextSplitter): LangChain text splitter.
    
    Example:
        ```python
        processor = LangChainDocumentProcessor()
        docs = processor.process_file_for_rag("contract.pdf", {"partner": "Restaurant"})
        ```
    """
    
    def __init__(self):
        """Initialize document processor with LangChain text splitter.
        
        Sets up DocumentProcessor and RecursiveCharacterTextSplitter with
        optimized configuration for financial documents.
        """
        self.base_processor = DocumentProcessor()
        
        # Use LangChain's RecursiveCharacterTextSplitter as required by Task 2
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Double newlines (paragraphs)
                "\n",    # Single newlines
                " ",     # Spaces
                ""       # Characters
            ]
        )
        
    def process_file_for_rag(self, file_path: str, document_metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Process files into LangChain Document objects for RAG integration.
        
        Args:
            file_path (str): Path to document file (PDF, TXT, MD).
            document_metadata (Optional[Dict[str, Any]]): Additional metadata
                for generated Document objects.
        
        Returns:
            List[Document]: LangChain Document objects with chunked content
                and comprehensive metadata.
        
        Raises:
            FileNotFoundError: File path does not exist.
            ValueError: Unsupported format or no extractable content.
            ProcessingError: Text extraction or splitting fails.
        
        Example:
            ```python
            docs = processor.process_file_for_rag(
                "contract.pdf", 
                {"partner_name": "Restaurant", "type": "contract"}
            )
            ```
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text using the existing processor
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            text = self.base_processor._extract_pdf_text(file_path)
        elif file_extension in ['.txt', '.md']:
            text = self.base_processor._extract_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        if not text.strip():
            raise ValueError("No text content found in the file")
        
        # Generate base metadata
        base_metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "file_type": file_extension,
            "processed_at": datetime.now().isoformat(),
            "total_characters": len(text),
        }
        
        if document_metadata:
            base_metadata.update(document_metadata)
        
        # Use LangChain's text splitter
        text_chunks = self.text_splitter.split_text(text)
        
        # Convert to LangChain Document objects
        documents = []
        for i, chunk in enumerate(text_chunks):
            # Add chunk-specific metadata
            chunk_metadata = {
                **base_metadata,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "chunk_id": f"{base_metadata['file_name']}_{i}",
                "chunk_size": len(chunk)
            }
            
            doc = Document(
                page_content=chunk,
                metadata=chunk_metadata
            )
            documents.append(doc)
        
        logger.info(f"Processed file '{file_path}' into {len(documents)} LangChain documents")
        return documents
    
    def process_text_for_rag(self, text: str, document_metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Process raw text and return LangChain Document objects for RAG pipeline.
        
        Args:
            text: Raw text content
            document_metadata: Additional metadata for the document
            
        Returns:
            List of LangChain Document objects with metadata
        """
        if not text.strip():
            raise ValueError("Text content cannot be empty")
        
        # Generate base metadata
        base_metadata = {
            "source": "text_input",
            "processed_at": datetime.now().isoformat(),
            "total_characters": len(text),
        }
        
        if document_metadata:
            base_metadata.update(document_metadata)
        
        # Use LangChain's text splitter
        text_chunks = self.text_splitter.split_text(text)
        
        # Convert to LangChain Document objects
        documents = []
        for i, chunk in enumerate(text_chunks):
            # Add chunk-specific metadata
            chunk_metadata = {
                **base_metadata,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "chunk_id": f"text_input_{i}",
                "chunk_size": len(chunk)
            }
            
            doc = Document(
                page_content=chunk,
                metadata=chunk_metadata
            )
            documents.append(doc)
        
        logger.info(f"Processed text into {len(documents)} LangChain documents")
        return documents
    
    def process_partner_documents(self, partner_name: str, document_dir: str = "data/sample_contracts") -> Dict[str, List[Document]]:
        """
        Process all documents for a specific partner (contract + payout reports).
        
        Args:
            partner_name: Name of the partner (e.g., "Sushi Express")
            document_dir: Directory containing the documents
            
        Returns:
            Dictionary with document types as keys and lists of Documents as values
        """
        partner_documents = {
            "contract": [],
            "payout_report": [],
            "other": []
        }
        
        if not os.path.exists(document_dir):
            logger.warning(f"Document directory '{document_dir}' not found")
            return partner_documents
        
        # Look for files related to this partner
        partner_key = partner_name.lower().replace(" ", "_").replace("-", "_")
        
        for filename in os.listdir(document_dir):
            if filename.endswith(('.txt', '.pdf')) and partner_key in filename.lower():
                file_path = os.path.join(document_dir, filename)
                
                # Determine document type based on filename
                if 'contract' in filename.lower():
                    doc_type = "contract"
                    doc_metadata = {
                        "document_type": "contract",
                        "partner_name": partner_name,
                        "title": f"{partner_name} Partnership Agreement"
                    }
                elif 'payout' in filename.lower() or 'report' in filename.lower():
                    doc_type = "payout_report"
                    doc_metadata = {
                        "document_type": "payout_report",
                        "partner_name": partner_name,
                        "title": f"{partner_name} Payout Report"
                    }
                else:
                    doc_type = "other"
                    doc_metadata = {
                        "document_type": "other",
                        "partner_name": partner_name,
                        "title": filename
                    }
                
                try:
                    documents = self.process_file_for_rag(file_path, doc_metadata)
                    partner_documents[doc_type].extend(documents)
                    logger.info(f"Processed {doc_type} '{filename}': {len(documents)} documents")
                except Exception as e:
                    logger.error(f"Failed to process '{filename}': {e}")
                    continue
        
        total_docs = sum(len(docs) for docs in partner_documents.values())
        logger.info(f"Processed all documents for '{partner_name}': {total_docs} total documents")
        
        return partner_documents


def test_langchain_processor():
    """Test the LangChain document processor."""
    processor = LangChainDocumentProcessor()
    
    # Test with Sushi Express documents
    partner_docs = processor.process_partner_documents("Sushi Express")
    
    print(f"🧪 LangChain Document Processor Test Results:")
    print(f"📄 Contract documents: {len(partner_docs['contract'])}")
    print(f"📊 Payout report documents: {len(partner_docs['payout_report'])}")
    print(f"📁 Other documents: {len(partner_docs['other'])}")
    
    # Show sample document
    if partner_docs['contract']:
        sample_doc = partner_docs['contract'][0]
        print(f"\n📋 Sample contract chunk:")
        print(f"Content (first 200 chars): {sample_doc.page_content[:200]}...")
        print(f"Metadata: {sample_doc.metadata}")
    
    return partner_docs


if __name__ == "__main__":
    test_langchain_processor()
