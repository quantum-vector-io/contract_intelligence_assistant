"""
Core RAG (Retrieval-Augmented Generation) service using LangChain for Task 2.
This implements the financial analyst RAG pipeline for contract discrepancy analysis.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import os
from datetime import datetime

from langchain.schema import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from src.services.langchain_document_service import LangChainDocumentProcessor
from src.services.opensearch_service import OpenSearchService
from src.core.config import settings
from src.core.prompts import EXPERT_ANALYST_PROMPT, ANALYSIS_REPORT_FORMAT, EXECUTIVE_SUMMARY_PROMPT, FINANCIAL_ANALYST_PROMPT_LEGACY, SIMPLE_DATABASE_QUERY_PROMPT

logger = logging.getLogger(__name__)


class FinancialAnalystRAGChain:
    """
    RAG chain specifically designed for financial analysis of contracts and payout reports.
    Acts as a financial analyst to identify discrepancies between legal contracts and financial reports.
    """
    
    def __init__(self):
        """Initialize the Financial Analyst RAG chain."""
        self.document_processor = LangChainDocumentProcessor()
        self.opensearch_service = OpenSearchService()
        
        # Initialize OpenAI components
        self.llm = ChatOpenAI(
            model_name="gpt-4",  # Use GPT-4 for better analytical capabilities
            temperature=0.1,     # Low temperature for consistent analysis
            openai_api_key=settings.openai_api_key,
            streaming=False      # Explicitly disable streaming to prevent character separation
        )
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=settings.openai_api_key
        )
        
        # Financial analyst prompts - now using centralized prompts
        self.expert_analyst_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=EXPERT_ANALYST_PROMPT
        )
        
        self.detailed_report_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=EXPERT_ANALYST_PROMPT + ANALYSIS_REPORT_FORMAT
        )
        
        self.executive_summary_prompt = PromptTemplate(
            input_variables=["context", "filename"],
            template=EXECUTIVE_SUMMARY_PROMPT
        )
        
        # Legacy prompt for backwards compatibility
        self.financial_analyst_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=FINANCIAL_ANALYST_PROMPT_LEGACY
        )
        
        # Simple database query prompt for basic information requests
        self.simple_database_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=SIMPLE_DATABASE_QUERY_PROMPT
        )
        
        self.partner_documents_cache = {}  # Cache for partner documents
        
    def _clean_response_text(self, text: str) -> str:
        """
        Clean up potential streaming artifacts in AI responses.
        
        Args:
            text: Raw AI response text
            
        Returns:
            Cleaned text without streaming artifacts
        """
        import re
        
        # Remove single character lines (streaming artifacts)
        lines = text.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip single character lines that are likely streaming artifacts
            if len(line) == 1 and line.isalnum():
                # Check if this single character should be part of the previous line
                if cleaned_lines and not cleaned_lines[-1].endswith(('.', '!', '?', ':')):
                    cleaned_lines[-1] += line
                continue
            
            # Skip empty lines between single characters
            if not line and i > 0 and i < len(lines) - 1:
                prev_line = lines[i-1].strip()
                next_line = lines[i+1].strip()
                if len(prev_line) == 1 and len(next_line) == 1:
                    continue
            
            cleaned_lines.append(line)
        
        # Join lines and fix common streaming artifacts
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Fix separated numbers and currency (e.g., "2\n,\n925.00" -> "2,925.00")
        cleaned_text = re.sub(r'(\d+)\s*\n\s*,\s*\n\s*(\d+)', r'\1,\2', cleaned_text)
        
        # Fix separated decimals (e.g., "925\n.\n00" -> "925.00")
        cleaned_text = re.sub(r'(\d+)\s*\n\s*\.\s*\n\s*(\d+)', r'\1.\2', cleaned_text)
        
        # Fix separated words ONLY if they are clearly streaming artifacts
        # Only fix single characters separated by newlines in specific patterns
        # Be much more conservative to avoid joining legitimate word boundaries
        
        # Fix obvious streaming artifacts like "w\ni\nt\nh" -> "with" but ONLY for very specific cases
        # Look for patterns where single characters are separated by newlines AND form common words
        streaming_patterns = [
            (r'\bw\s*\n\s*i\s*\n\s*t\s*\n\s*h\b', 'with'),
            (r'\bf\s*\n\s*r\s*\n\s*o\s*\n\s*m\b', 'from'),
            (r'\bt\s*\n\s*h\s*\n\s*e\s*\n\s*r\s*\n\s*e\b', 'there'),
            (r'\bt\s*\n\s*h\s*\n\s*a\s*\n\s*t\b', 'that'),
            (r'\bt\s*\n\s*h\s*\n\s*i\s*\n\s*s\b', 'this'),
        ]
        
        for pattern, replacement in streaming_patterns:
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
        
        # DO NOT use the overly aggressive patterns that join any two characters
        # The old patterns were causing legitimate words to be joined incorrectly
        
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        
        return cleaned_text.strip()
        
    def _is_simple_database_query(self, question: str) -> bool:
        """
        Detect if a question is a simple database query that should use simple response format.
        
        Args:
            question: The user's question
            
        Returns:
            True if it's a simple query, False if it needs complex analysis
        """
        question_lower = question.lower().strip()
        
        # Keywords indicating simple informational queries
        simple_query_patterns = [
            'list', 'names', 'show me', 'what are', 'which', 'how many',
            'all restaurants', 'all partners', 'all documents',
            'restaurant names', 'partner names', 'document names',
            'from db', 'in database', 'available', 'stored'
        ]
        
        # Check if the question contains simple query patterns
        for pattern in simple_query_patterns:
            if pattern in question_lower:
                return True
                
        # Complex analysis indicators - if these are present, use financial analysis
        complex_query_patterns = [
            'analyze', 'discrepancy', 'compare', 'calculate', 'reconcile',
            'payout', 'commission', 'fee', 'penalty', 'financial', 'money',
            'difference', 'variance', 'explanation', 'why', 'how much'
        ]
        
        for pattern in complex_query_patterns:
            if pattern in question_lower:
                return False
                
        # If question is very short and simple, treat as simple query
        if len(question_lower.split()) <= 5:
            return True
            
        return False
        
    def load_partner_documents(self, partner_name: str) -> Dict[str, List[Document]]:
        """
        Load all documents for a specific partner from OpenSearch index.
        
        Args:
            partner_name: Name of the partner
            
        Returns:
            Dictionary with document types and their respective documents
        """
        if partner_name in self.partner_documents_cache:
            logger.info(f"Using cached documents for partner: {partner_name}")
            return self.partner_documents_cache[partner_name]
        
        # Search for documents by partner name in OpenSearch
        try:
            logger.info(f"DEBUG: Searching for documents with partner_name: '{partner_name}'")
            search_body = {
                "size": 100,  # Increase to get all chunks
                "query": {
                    "match": {
                        "partner_name": partner_name
                    }
                },
                "_source": ["content", "document_type", "partner_name", "chunk_id"]
            }
            
            logger.info(f"DEBUG: Search query: {search_body}")
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            total_hits = response["hits"]["total"]["value"]
            logger.info(f"DEBUG: Found {total_hits} documents in OpenSearch")
            
            partner_docs = {"contract": [], "payout_report": [], "other": []}
            
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                doc_type = source.get("document_type", "other")
                
                # Create LangChain Document
                doc = Document(
                    page_content=source.get("content", ""),
                    metadata={
                        "document_type": doc_type,
                        "partner_name": partner_name,
                        "chunk_id": source.get("chunk_id", "")
                    }
                )
                
                if doc_type in partner_docs:
                    partner_docs[doc_type].append(doc)
                else:
                    partner_docs["other"].append(doc)
            
            # Cache the results
            self.partner_documents_cache[partner_name] = partner_docs
            
            total_docs = sum(len(docs) for docs in partner_docs.values())
            logger.info(f"Loaded {total_docs} documents for partner: {partner_name}")
            
            return partner_docs
            
        except Exception as e:
            logger.error(f"Error loading documents for partner {partner_name}: {e}")
            return {"contract": [], "payout_report": [], "other": []}
    
    def create_retrieval_context(self, partner_name: str, query: str, max_docs: int = 10) -> str:
        """
        Create context by retrieving relevant documents for a partner based on the query.
        
        Args:
            partner_name: Name of the partner
            query: The question/query to find relevant context for
            max_docs: Maximum number of document chunks to include
            
        Returns:
            Formatted context string with relevant document excerpts
        """
        partner_docs = self.load_partner_documents(partner_name)
        
        # Combine all documents for the partner
        all_docs = []
        for doc_type, docs in partner_docs.items():
            all_docs.extend(docs)
        
        if not all_docs:
            raise ValueError(f"No documents found for partner: {partner_name}")
        
        # Enhanced retrieval logic to ensure both document types are included
        contract_docs = partner_docs.get("contract", [])
        payout_docs = partner_docs.get("payout_report", [])
        other_docs = partner_docs.get("other", [])
        
        # If we have both contract and payout documents, ensure representation from both
        if contract_docs and payout_docs:
            # Take best contract chunks (up to half of max_docs)
            contract_limit = max(1, max_docs // 2)
            payout_limit = max(1, max_docs - contract_limit)
            
            # Score contract documents
            query_keywords = set(query.lower().split())
            
            def score_document(doc):
                content_keywords = set(doc.page_content.lower().split())
                return len(query_keywords.intersection(content_keywords))
            
            # Get top contract chunks
            contract_scored = [(score_document(doc), doc) for doc in contract_docs]
            contract_scored.sort(key=lambda x: x[0], reverse=True)
            selected_contracts = [doc for score, doc in contract_scored[:contract_limit]]
            
            # Get top payout chunks
            payout_scored = [(score_document(doc), doc) for doc in payout_docs]
            payout_scored.sort(key=lambda x: x[0], reverse=True)
            selected_payouts = [doc for score, doc in payout_scored[:payout_limit]]
            
            # Combine selected documents
            relevant_docs = selected_contracts + selected_payouts
            
            logger.info(f"Multi-document retrieval: {len(selected_contracts)} contract chunks, {len(selected_payouts)} payout chunks")
            
        else:
            # Standard keyword-based scoring for single document type
            query_keywords = set(query.lower().split())
            
            scored_docs = []
            for doc in all_docs:
                content_keywords = set(doc.page_content.lower().split())
                score = len(query_keywords.intersection(content_keywords))
                scored_docs.append((score, doc))
            
            # Sort by relevance score and take top documents
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            relevant_docs = [doc for score, doc in scored_docs[:max_docs] if score > 0]
            
            # If no keyword matches, take the first few documents
            if not relevant_docs:
                relevant_docs = all_docs[:max_docs]
        
        # Format context
        context_parts = []
        for i, doc in enumerate(relevant_docs):
            doc_type = doc.metadata.get('document_type', 'unknown')
            context_parts.append(
                f"DOCUMENT {i+1} ({doc_type.upper()}):\n"
                f"Source: {doc.metadata.get('file_name', 'unknown')}\n"
                f"Content: {doc.page_content}\n"
                f"---"
            )
        
        context = "\n\n".join(context_parts)
        logger.info(f"Created context with {len(relevant_docs)} relevant documents")
        
        return context
    
    def analyze_contract_discrepancies(self, partner_name: str, specific_question: Optional[str] = None, detailed_report: bool = False) -> str:
        """
        Analyze discrepancies between a partner's contract and payout reports.
        
        Args:
            partner_name: Name of the partner to analyze
            specific_question: Optional specific question to focus the analysis
            detailed_report: If True, use detailed report format
            
        Returns:
            Detailed financial analysis explaining discrepancies
        """
        # Default question if none provided
        if not specific_question:
            specific_question = f"Explain the discrepancies in the payout report for {partner_name} based on the provided contract. Identify the service fees and penalties that cause differences in the payout amounts."
        
        try:
            # Create retrieval context
            context = self.create_retrieval_context(partner_name, specific_question)
            
            # Use the new expert analyst method
            analysis = self.analyze_with_expert_prompt(context, specific_question, detailed_report)
            
            logger.info(f"Generated discrepancy analysis for partner: {partner_name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing discrepancies for {partner_name}: {e}")
            raise
    
    def get_partner_summary(self, partner_name: str) -> Dict[str, Any]:
        """
        Get a summary of available documents for a partner.
        
        Args:
            partner_name: Name of the partner
            
        Returns:
            Summary of partner documents and metadata
        """
        partner_docs = self.load_partner_documents(partner_name)
        
        summary = {
            "partner_name": partner_name,
            "total_documents": sum(len(docs) for docs in partner_docs.values()),
            "document_types": {},
            "last_processed": datetime.now().isoformat()
        }
        
        for doc_type, docs in partner_docs.items():
            if docs:
                summary["document_types"][doc_type] = {
                    "count": len(docs),
                    "files": list(set(doc.metadata.get('file_name', 'unknown') for doc in docs)),
                    "total_content_length": sum(len(doc.page_content) for doc in docs)
                }
        
        return summary

    def query_all_documents(self, question: str, max_docs: int = 15) -> str:
        """
        Query across all documents in the database, not limited to a specific partner.
        
        Args:
            question: The question to search for
            max_docs: Maximum number of document chunks to include
            
        Returns:
            AI analysis based on relevant documents from across the database
        """
        try:
            # Search across all documents using semantic search
            search_body = {
                "size": max_docs,
                "query": {
                    "match_all": {}  # Get all documents, we'll filter by relevance
                },
                "_source": ["content", "document_type", "partner_name", "chunk_id", "file_name"]
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            # Convert to LangChain documents
            all_docs = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                doc = Document(
                    page_content=source.get("content", ""),
                    metadata={
                        "document_type": source.get("document_type", "unknown"),
                        "partner_name": source.get("partner_name", "unknown"),
                        "chunk_id": source.get("chunk_id", ""),
                        "file_name": source.get("file_name", "unknown")
                    }
                )
                all_docs.append(doc)
            
            if not all_docs:
                return "No documents found in the database."
            
            # Simple relevance scoring based on keyword overlap
            query_keywords = set(question.lower().split())
            
            scored_docs = []
            for doc in all_docs:
                content_keywords = set(doc.page_content.lower().split())
                score = len(query_keywords.intersection(content_keywords))
                scored_docs.append((score, doc))
            
            # Sort by relevance score and take top documents
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            relevant_docs = [doc for score, doc in scored_docs[:max_docs] if score > 0]
            
            # If no keyword matches, take some documents anyway
            if not relevant_docs:
                relevant_docs = all_docs[:5]
            
            # Format context for analysis
            context_parts = []
            for i, doc in enumerate(relevant_docs):
                doc_type = doc.metadata.get('document_type', 'unknown')
                partner = doc.metadata.get('partner_name', 'unknown')
                context_parts.append(
                    f"DOCUMENT {i+1} ({doc_type.upper()}) - Partner: {partner}:\n"
                    f"Content: {doc.page_content}\n"
                    f"---"
                )
            
            context = "\n\n".join(context_parts)
            
            # Choose appropriate prompt based on query type
            is_simple_query = self._is_simple_database_query(question)
            
            if is_simple_query:
                # Use simple database prompt for basic informational queries
                prompt_to_use = self.simple_database_prompt
                logger.info(f"Using simple database prompt for query: {question}")
            else:
                # Use financial analyst prompt for complex analysis
                prompt_to_use = self.financial_analyst_prompt
                logger.info(f"Using financial analyst prompt for query: {question}")
            
            # Generate analysis using the appropriate prompt
            response = self.llm.invoke(
                prompt_to_use.format(
                    context=context,
                    question=question
                )
            )
            
            analysis = response.content if hasattr(response, 'content') else str(response)
            
            # Clean up any potential streaming artifacts
            analysis = self._clean_response_text(analysis)
            
            logger.info(f"Generated database query analysis for: {question}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error querying all documents: {e}")
            raise

    def query_partner_documents(self, partner_name: str, question: str, max_docs: int = 10) -> str:
        """
        Query documents for a specific partner only.
        
        Args:
            partner_name: Name of the partner to search documents for
            question: The question to search for
            max_docs: Maximum number of document chunks to include
            
        Returns:
            AI analysis based on relevant documents from the specific partner only
        """
        try:
            logger.info(f"Querying documents for partner: {partner_name}")
            
            # Search for documents matching the specific partner name
            search_body = {
                "size": max_docs,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "partner_name": partner_name
                                }
                            }
                        ]
                    }
                },
                "_source": ["content", "document_type", "partner_name", "chunk_id", "file_name"]
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            # Convert to LangChain documents
            partner_docs = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                doc = Document(
                    page_content=source.get("content", ""),
                    metadata={
                        "document_type": source.get("document_type", "unknown"),
                        "partner_name": source.get("partner_name", "unknown"),
                        "chunk_id": source.get("chunk_id", ""),
                        "file_name": source.get("file_name", "unknown")
                    }
                )
                partner_docs.append(doc)
            
            if not partner_docs:
                return f"No documents found for partner: {partner_name}. Please upload documents for this partner first."
            
            # Simple relevance scoring based on keyword overlap
            query_keywords = set(question.lower().split())
            
            scored_docs = []
            for doc in partner_docs:
                content_keywords = set(doc.page_content.lower().split())
                score = len(query_keywords.intersection(content_keywords))
                scored_docs.append((score, doc))
            
            # Sort by relevance score and take top documents
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            relevant_docs = [doc for score, doc in scored_docs[:max_docs] if score > 0]
            
            # If no keyword matches, take some documents anyway
            if not relevant_docs:
                relevant_docs = partner_docs[:max_docs]
            
            # Format context for analysis
            context_parts = []
            for i, doc in enumerate(relevant_docs):
                doc_type = doc.metadata.get('document_type', 'unknown')
                file_name = doc.metadata.get('file_name', 'unknown')
                context_parts.append(
                    f"DOCUMENT {i+1} ({doc_type.upper()}) - {file_name}:\n"
                    f"Content: {doc.page_content}\n"
                    f"---"
                )
            
            context = "\n\n".join(context_parts)
            
            # Generate analysis using the financial analyst prompt
            response = self.llm.invoke(
                self.financial_analyst_prompt.format(
                    context=context,
                    question=question
                )
            )
            
            analysis = response.content if hasattr(response, 'content') else str(response)
            
            # Clean up any potential streaming artifacts
            analysis = self._clean_response_text(analysis)
            
            logger.info(f"Generated partner-specific analysis for {partner_name}: {question}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error querying partner documents for {partner_name}: {e}")
            raise

    def query_session_documents(self, session_id: str, question: str, max_docs: int = 10, detailed_report: bool = False) -> str:
        """
        Query documents for a specific session only (newly uploaded documents).
        
        Args:
            session_id: Session ID of the uploaded documents
            question: The question to search for
            max_docs: Maximum number of document chunks to include
            
        Returns:
            AI analysis based on relevant documents from the specific session only
        """
        try:
            logger.info(f"Querying documents for session: {session_id}")
            
            # Search for documents matching the specific session ID
            search_body = {
                "size": max_docs,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "session_id": session_id
                                }
                            }
                        ]
                    }
                },
                "_source": ["content", "document_type", "partner_name", "chunk_id", "file_name", "session_id"]
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            # Convert to LangChain documents
            session_docs = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                doc = Document(
                    page_content=source.get("content", ""),
                    metadata={
                        "document_type": source.get("document_type", "unknown"),
                        "partner_name": source.get("partner_name", "unknown"),
                        "chunk_id": source.get("chunk_id", ""),
                        "file_name": source.get("file_name", "unknown"),
                        "session_id": source.get("session_id", "")
                    }
                )
                session_docs.append(doc)
            
            if not session_docs:
                return f"No documents found for this upload session. Please try uploading the documents again."
            
            # Simple relevance scoring based on keyword overlap
            query_keywords = set(question.lower().split())
            
            scored_docs = []
            for doc in session_docs:
                content_keywords = set(doc.page_content.lower().split())
                score = len(query_keywords.intersection(content_keywords))
                scored_docs.append((score, doc))
            
            # Sort by relevance score and take top documents
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            relevant_docs = [doc for score, doc in scored_docs[:max_docs] if score > 0]
            
            # If no keyword matches, take all session documents
            if not relevant_docs:
                relevant_docs = session_docs[:max_docs]
            
            # Format context for analysis - only show uploaded files
            context_parts = []
            for i, doc in enumerate(relevant_docs):
                doc_type = doc.metadata.get('document_type', 'unknown')
                file_name = doc.metadata.get('file_name', 'unknown')
                context_parts.append(
                    f"DOCUMENT {i+1} ({doc_type.upper()}) - {file_name}:\n"
                    f"Content: {doc.page_content}\n"
                    f"---"
                )
            
            context = "\n\n".join(context_parts)
            
            # Use the new expert analyst method
            analysis = self.analyze_with_expert_prompt(context, question, detailed_report)
            
            logger.info(f"Generated session-specific analysis for session {session_id}: {question}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error querying session documents for {session_id}: {e}")
            raise

    def generate_executive_summary(self, session_id: str, filename: str) -> str:
        """
        Generate an executive summary for a newly uploaded document.
        
        Args:
            session_id: Session ID of the uploaded document
            filename: Original filename for display purposes
            
        Returns:
            Executive summary of the document
        """
        try:
            logger.info(f"Generating executive summary for: {filename}")
            
            # Search for documents matching the specific session ID
            search_body = {
                "size": 5,  # Limit to first few chunks for summary
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "session_id": session_id
                                }
                            }
                        ]
                    }
                },
                "_source": ["content", "document_type", "partner_name", "chunk_id", "file_name", "session_id"]
            }
            
            response = self.opensearch_service.client.search(
                index=self.opensearch_service.index_name,
                body=search_body
            )
            
            if not response["hits"]["hits"]:
                return f"No content found for {filename}. Please try uploading again."
            
            # Combine content from all chunks
            content_parts = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                content_parts.append(source.get("content", ""))
            
            context = "\n\n".join(content_parts)
            
            # Generate summary using the executive summary prompt
            response = self.llm.invoke(
                self.executive_summary_prompt.format(
                    context=context,
                    filename=filename
                )
            )
            
            summary = response.content if hasattr(response, 'content') else str(response)
            
            # Clean up any potential streaming artifacts
            summary = self._clean_response_text(summary)
            
            logger.info(f"Generated executive summary for: {filename}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating executive summary for {filename}: {e}")
            raise

    def analyze_with_expert_prompt(self, context: str, question: str, detailed_report: bool = False) -> str:
        """
        Analyze using the expert analyst prompt with optional detailed report format.
        
        Args:
            context: Document context for analysis
            question: User's question
            detailed_report: If True, use detailed report format
            
        Returns:
            Analysis response (concise or detailed based on parameter)
        """
        try:
            # Choose prompt based on detailed_report parameter
            if detailed_report:
                prompt_template = self.detailed_report_prompt
                logger.info("Using detailed report format")
            else:
                prompt_template = self.expert_analyst_prompt
                logger.info("Using concise expert analyst format")
            
            # Generate analysis
            response = self.llm.invoke(
                prompt_template.format(
                    context=context,
                    question=question
                )
            )
            
            analysis = response.content if hasattr(response, 'content') else str(response)
            
            # Clean up any potential streaming artifacts
            analysis = self._clean_response_text(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in expert analysis: {e}")
            raise


def test_rag_chain():
    """Test the Financial Analyst RAG chain with Sushi Express documents."""
    print("🧪 Testing Financial Analyst RAG Chain")
    print("=" * 50)
    
    rag_chain = FinancialAnalystRAGChain()
    
    # Test partner summary
    print("\n1️⃣ Getting partner summary...")
    summary = rag_chain.get_partner_summary("Sushi Express")
    print(f"📊 Partner: {summary['partner_name']}")
    print(f"📄 Total documents: {summary['total_documents']}")
    print(f"📋 Document types: {list(summary['document_types'].keys())}")
    
    # Test discrepancy analysis
    print("\n2️⃣ Analyzing contract discrepancies...")
    try:
        analysis = rag_chain.analyze_contract_discrepancies(
            "Sushi Express",
            "Explain the discrepancies in this payout report based on the provided contract."
        )
        print(f"✅ Analysis generated ({len(analysis)} characters)")
        print("\n📋 FINANCIAL ANALYSIS:")
        print("-" * 40)
        print(analysis)
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RAG Chain test complete!")


if __name__ == "__main__":
    test_rag_chain()
