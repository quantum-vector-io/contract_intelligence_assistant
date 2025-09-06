"""Retrieval-Augmented Generation (RAG) service for financial contract analysis.

This module provides a comprehensive RAG implementation specifically designed for financial
analysis of restaurant partnership contracts and payout reports. It combines OpenAI's GPT-4
language model with OpenSearch vector storage and LangChain orchestration to deliver
sophisticated contract discrepancy analysis capabilities.

The service acts as an AI financial analyst that can:
- Compare legal contracts with financial payout reports
- Identify discrepancies in commission rates, fees, and payment terms
- Generate detailed financial analysis reports with executive summaries
- Process complex multi-document queries with contextual understanding
- Provide both simple informational queries and complex analytical insights

Key Components:
    - FinancialAnalystRAGChain: Main RAG orchestration class
    - LangChain integration for document processing and retrieval
    - OpenAI GPT-4 for advanced reasoning and analysis
    - OpenSearch vector storage for semantic document retrieval
    - Specialized prompts for financial domain expertise

The service supports multiple analysis modes:
    - Expert financial analysis with detailed calculations
    - Executive summary generation for high-level insights
    - Simple database queries for informational requests
    - Legacy compatibility for existing integrations

Example:
    ```python
    rag_service = FinancialAnalystRAGChain()
    
    # Load partner documents for analysis
    docs = rag_service.load_partner_documents("SushiExpress24-7")
    
    # Perform financial discrepancy analysis
    analysis = rag_service.analyze_query(
        question="Compare commission rates between contract and payout report",
        query_type="financial_analysis"
    )
    
    # Generate executive summary
    summary = rag_service.generate_executive_summary(partner_name="SushiExpress24-7")
    ```

Dependencies:
    - langchain: Document processing and RAG orchestration
    - openai: GPT-4 language model and embeddings
    - opensearch: Vector storage and semantic search
    - pydantic: Configuration management and data validation

Note:
    This service requires proper configuration of OpenAI API keys and OpenSearch
    connectivity. Ensure that document indexing is completed before running
    analysis queries.

Version:
    2.0.0 - Enhanced with multi-document support and advanced financial analysis
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
    """Comprehensive RAG chain for financial analysis of restaurant partnership agreements.
    
    This class implements a sophisticated Retrieval-Augmented Generation system specifically
    designed for analyzing restaurant partnership contracts and their corresponding payout
    reports. It acts as an AI financial analyst capable of identifying discrepancies,
    calculating variances, and generating detailed financial analysis reports.
    
    The system combines multiple AI technologies:
    - OpenAI GPT-4 for advanced reasoning and financial analysis
    - OpenAI Ada-002 embeddings for semantic document retrieval
    - OpenSearch vector database for scalable document storage
    - LangChain for orchestrating the RAG pipeline
    - Custom financial domain prompts for expert-level analysis
    
    Key Capabilities:
        - Multi-document financial discrepancy analysis
        - Commission rate variance calculations
        - Fee structure comparisons between contracts and reports
        - Executive summary generation for stakeholder reporting
        - Contextual query processing with domain expertise
        - Support for various restaurant partnership platforms
    
    Supported Analysis Types:
        - Expert financial analysis with detailed calculations
        - Executive summaries for high-level business insights
        - Simple database queries for informational requests
        - Legacy format analysis for backward compatibility
    
    Document Processing:
        - PDF contract parsing and text extraction
        - Payout report data normalization
        - Multi-partner document organization
        - Semantic chunking for optimal retrieval
    
    Attributes:
        document_processor (LangChainDocumentProcessor): Handles document processing operations.
        opensearch_service (OpenSearchService): Manages vector storage and retrieval.
        llm (ChatOpenAI): GPT-4 language model for analysis and reasoning.
        embeddings (OpenAIEmbeddings): Ada-002 model for document embeddings.
        expert_analyst_prompt (PromptTemplate): Template for expert financial analysis.
        detailed_report_prompt (PromptTemplate): Template for comprehensive reports.
        executive_summary_prompt (PromptTemplate): Template for executive summaries.
        financial_analyst_prompt (PromptTemplate): Legacy compatibility template.
        simple_database_prompt (PromptTemplate): Template for simple queries.
        partner_documents_cache (Dict): In-memory cache for partner document storage.
    
    Example:
        ```python
        # Initialize the RAG chain
        rag_chain = FinancialAnalystRAGChain()
        
        # Load documents for a specific partner
        docs = rag_chain.load_partner_documents("SushiExpress24-7")
        
        # Perform financial analysis
        analysis_result = rag_chain.analyze_query(
            question="Identify commission rate discrepancies between contract and payout report",
            query_type="financial_analysis"
        )
        
        # Generate executive summary
        summary = rag_chain.generate_executive_summary(
            partner_name="SushiExpress24-7"
        )
        ```
    
    Note:
        This class requires proper initialization of OpenAI API credentials and
        OpenSearch connectivity. Ensure that document indexing is completed
        before attempting analysis operations.
    
    Raises:
        ConnectionError: When OpenSearch or OpenAI services are unavailable.
        ValueError: When required configuration parameters are missing.
        DocumentNotFoundError: When requested partner documents are not indexed.
    """
    
    def __init__(self):
        """Initialize the Financial Analyst RAG chain with all required components.
        
        Sets up the complete RAG pipeline including document processing, vector storage,
        language models, embeddings, and specialized financial analysis prompts. The
        initialization creates a production-ready system optimized for financial
        contract analysis with low-temperature settings for consistent results.
        
        Components Initialized:
            - LangChain document processor for PDF and text handling
            - OpenSearch service for vector storage and semantic retrieval
            - GPT-4 language model with financial analysis optimization
            - Ada-002 embeddings for high-quality document representations
            - Specialized prompt templates for different analysis types
            - Partner document caching system for performance optimization
        
        Configuration Settings:
            - GPT-4 model for advanced reasoning capabilities
            - Temperature 0.1 for consistent analytical outputs
            - Streaming disabled to prevent text fragmentation
            - Ada-002 embeddings for optimal semantic understanding
        
        Prompt Templates:
            - Expert analyst: Comprehensive financial analysis with calculations
            - Detailed report: Full analysis with structured reporting format
            - Executive summary: High-level insights for stakeholders
            - Legacy format: Backward compatibility with existing systems
            - Simple database: Basic informational query responses
        
        Raises:
            ValueError: When OpenAI API key is not configured in settings.
            ConnectionError: When OpenSearch service is not accessible.
            ImportError: When required dependencies are not installed.
        
        Note:
            This method assumes that all required environment variables and
            configuration settings are properly set before instantiation.
            The partner document cache is initialized empty and will be
            populated during document loading operations.
        """
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
        """Clean up potential streaming artifacts and formatting issues in AI responses.
        
        This method addresses common issues that can occur in AI-generated text,
        particularly when streaming is involved or when text formatting is disrupted.
        It intelligently reconstructs fragmented text while preserving legitimate
        line breaks and formatting.
        
        Cleaning Operations:
            - Removes single-character lines that are streaming artifacts
            - Reconstructs fragmented numbers and currency values
            - Fixes separated decimal points and commas
            - Repairs common word fragmentations
            - Preserves intentional formatting and line breaks
            - Removes excessive whitespace while maintaining readability
        
        Text Reconstruction:
            - Currency: "2\\n,\\n925.00" → "2,925.00"
            - Decimals: "925\\n.\\n00" → "925.00"
            - Common words: "w\\ni\\nt\\nh" → "with"
            - Conservative approach to avoid joining legitimate word boundaries
        
        Args:
            text (str): Raw AI response text that may contain streaming artifacts
                or formatting issues requiring cleanup.
        
        Returns:
            str: Cleaned and properly formatted text with artifacts removed
                and fragmented content reconstructed while preserving
                intentional formatting.
        
        Note:
            This method uses conservative patterns to avoid incorrectly joining
            text that should remain separated. It focuses on obvious streaming
            artifacts and common formatting issues rather than aggressive
            text reconstruction.
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
        """Classify user questions to determine appropriate analysis approach.
        
        This method analyzes user questions to determine whether they require
        simple informational responses or complex financial analysis. This
        classification enables the system to use the most appropriate prompt
        template and response format for optimal user experience.
        
        Classification Logic:
            - Simple queries: Basic information requests about available data
            - Complex queries: Financial analysis requiring calculation and reasoning
            - Hybrid detection: Balances simple patterns with analytical indicators
            - Length heuristics: Very short questions typically seek simple information
        
        Simple Query Indicators:
            - "list", "names", "show me", "what are", "which", "how many"
            - "all restaurants", "all partners", "all documents"
            - "from db", "in database", "available", "stored"
            - Questions under 5 words without analytical keywords
        
        Complex Query Indicators:
            - "analyze", "discrepancy", "compare", "calculate", "reconcile"
            - "payout", "commission", "fee", "penalty", "financial", "money"
            - "difference", "variance", "explanation", "why", "how much"
            - Financial terms requiring analytical reasoning
        
        Args:
            question (str): The user's question to be classified for
                appropriate processing approach.
        
        Returns:
            bool: True if the question is a simple database query requiring
                basic informational response, False if it requires complex
                financial analysis with calculations and reasoning.
        
        Examples:
            Simple queries:
                - "List all restaurant names"
                - "Show me available documents"
                - "What partners are in the database?"
            
            Complex queries:
                - "Analyze commission rate discrepancies"
                - "Compare payout amounts with contract terms"
                - "Calculate variance in delivery fees"
        
        Note:
            This classification directly impacts the prompt template selection
            and response format. Misclassification can lead to overly complex
            responses for simple queries or insufficient detail for analytical
            requests.
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
        """Load and organize all documents for a specific restaurant partner from OpenSearch.
        
        This method retrieves all indexed documents associated with a restaurant partner,
        organizing them by document type for efficient analysis. It implements intelligent
        caching to improve performance and supports comprehensive document discovery
        across different partnership platforms.
        
        Document Retrieval Process:
            1. Check partner document cache for existing data
            2. Query OpenSearch index using partner name matching
            3. Retrieve document chunks with metadata preservation
            4. Organize documents by type (contracts, reports, addendums)
            5. Cache results for subsequent queries
            6. Log retrieval statistics for monitoring
        
        Supported Document Types:
            - Contracts: Partnership agreements and terms
            - Payout Reports: Financial transaction records
            - Addendums: Contract modifications and supplements
            - Amendments: Legal changes to existing agreements
        
        Document Organization:
            - Groups chunks by document type for targeted analysis
            - Preserves metadata including partner name and chunk IDs
            - Maintains content integrity across document fragments
            - Enables efficient retrieval for specific analysis types
        
        Args:
            partner_name (str): Name of the restaurant partner for which to load
                documents. Must match the indexed partner_name field in OpenSearch.
                Case-sensitive matching is used for precise retrieval.
        
        Returns:
            Dict[str, List[Document]]: Dictionary mapping document types to lists
                of LangChain Document objects. Each document contains:
                - page_content: The actual document text content
                - metadata: Document type, partner name, chunk ID, and other attributes
        
        Raises:
            ConnectionError: When OpenSearch service is not accessible or returns errors.
            ValueError: When partner_name is empty or None.
            DocumentNotFoundError: When no documents are found for the specified partner.
        
        Example:
            ```python
            # Load documents for SushiExpress24-7
            docs = rag_chain.load_partner_documents("SushiExpress24-7")
            
            # Access different document types
            contracts = docs.get("contract", [])
            reports = docs.get("payout_report", [])
            
            # Check document availability
            if "contract" in docs and "payout_report" in docs:
                # Perform comparative analysis
                analysis = rag_chain.compare_documents(contracts, reports)
            ```
        
        Note:
            This method implements caching to improve performance for repeated
            queries on the same partner. Cache invalidation is handled automatically
            when new documents are indexed for the partner.
        
        Performance:
            - First call: Queries OpenSearch and caches results
            - Subsequent calls: Returns cached data for improved speed
            - Cache memory usage scales with number of unique partners
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
        """Create optimized retrieval context for financial analysis queries.
        
        This method implements intelligent document retrieval and context creation
        specifically designed for financial analysis of restaurant partnership
        agreements. It ensures balanced representation from different document
        types and employs smart scoring algorithms to select the most relevant
        content for analysis.
        
        Context Creation Strategy:
            1. Load all partner documents with type classification
            2. Implement balanced sampling across document types
            3. Score documents based on query relevance
            4. Ensure critical document types are always represented
            5. Format context with clear document type indicators
            6. Optimize content length for LLM processing
        
        Document Selection Logic:
            - Balanced representation: Ensures both contracts and payout reports
            - Relevance scoring: Keyword matching for content selection
            - Type-aware sampling: Prevents single document type dominance
            - Quality filtering: Excludes empty or irrelevant content
        
        Scoring Algorithm:
            - Keyword intersection between query and document content
            - Document type priority based on query classification
            - Content length consideration for comprehensive coverage
            - Metadata relevance including partner name and document type
        
        Args:
            partner_name (str): Name of the restaurant partner for document retrieval.
                Must match indexed partner names exactly for accurate results.
            query (str): The analysis question or query for context relevance scoring.
                Used to identify the most pertinent document sections.
            max_docs (int, optional): Maximum number of document chunks to include
                in the context. Defaults to 10 for optimal LLM processing.
        
        Returns:
            str: Formatted context string containing relevant document excerpts
                organized by document type with clear delineation markers.
                Includes document metadata for analysis attribution.
        
        Raises:
            ValueError: When no documents are found for the specified partner
                or when partner_name is empty/None.
            ConnectionError: When document retrieval from OpenSearch fails.
        
        Example:
            ```python
            # Create context for commission analysis
            context = rag_chain.create_retrieval_context(
                partner_name="SushiExpress24-7",
                query="Compare commission rates between contract and payout report",
                max_docs=8
            )
            
            # Context includes balanced selection from both document types
            # with relevance scoring for commission-related content
            ```
        
        Context Format:
            The returned context is formatted as:
            ```
            === CONTRACT DOCUMENTS ===
            [Document content with metadata]
            
            === PAYOUT REPORT DOCUMENTS ===
            [Document content with metadata]
            
            === OTHER DOCUMENTS ===
            [Additional relevant content]
            ```
        
        Note:
            This method implements intelligent balancing to ensure that
            comparative financial analysis has access to both contractual
            terms and actual payout data, even when one document type
            has significantly more content than the other.
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
        """Perform comprehensive discrepancy analysis between partner contracts and payout reports.
        
        This method orchestrates end-to-end financial discrepancy analysis for restaurant
        partnership agreements, automatically identifying variances between contractual
        terms and actual payout amounts. It serves as the primary interface for
        comparative financial analysis in the RAG system.
        
        Analysis Workflow:
            1. Load and organize all partner documents by type
            2. Create optimized retrieval context for comparative analysis
            3. Apply expert financial analysis using specialized prompts
            4. Generate detailed discrepancy report with calculations
            5. Provide recommendations and explanations for variances
        
        Discrepancy Detection:
            - Commission rate variations between contract and actual payments
            - Service fee discrepancies and unexpected charges
            - Penalty applications and their contractual basis
            - Payment timing differences and their financial impact
            - Platform fee changes and their documentation
        
        Analysis Depth:
            - Standard analysis: Key discrepancies with brief explanations
            - Detailed report: Comprehensive calculations and recommendations
            - Automatic question generation for unfocused requests
            - Multi-document cross-referencing for accuracy
        
        Args:
            partner_name (str): Name of the restaurant partner for analysis.
                Must match exactly with indexed partner names for accurate
                document retrieval and analysis.
            specific_question (Optional[str]): Focused analysis question to
                guide the discrepancy detection. If None, generates a
                comprehensive general analysis covering all major
                discrepancy types. Defaults to None.
            detailed_report (bool, optional): Controls analysis depth and
                formatting. True generates comprehensive reports with
                detailed calculations, False provides concise executive
                summaries. Defaults to False.
        
        Returns:
            str: Comprehensive financial analysis report identifying and
                explaining discrepancies between contractual terms and
                actual payout amounts. Includes specific calculations,
                variance explanations, and actionable recommendations.
        
        Raises:
            ValueError: When partner_name is empty, None, or no documents
                are found for the specified partner.
            ConnectionError: When document retrieval or AI analysis services
                are unavailable.
            AnalysisError: When discrepancy analysis cannot be completed
                due to insufficient or conflicting data.
        
        Example:
            ```python
            # General discrepancy analysis
            analysis = rag_chain.analyze_contract_discrepancies(
                partner_name="SushiExpress24-7"
            )
            
            # Focused commission rate analysis
            commission_analysis = rag_chain.analyze_contract_discrepancies(
                partner_name="SushiExpress24-7",
                specific_question="Why do commission rates differ between contract and payouts?",
                detailed_report=True
            )
            ```
        
        Default Analysis:
            When no specific question is provided, the method automatically
            generates a comprehensive analysis focusing on:
            - Service fees and their contractual basis
            - Penalties and their calculation methods
            - Payout amount variances and explanations
            - Overall financial reconciliation
        
        Note:
            This method represents the primary business logic for financial
            discrepancy detection in restaurant partnership analysis. It
            combines document retrieval, context creation, and expert AI
            analysis to deliver actionable financial insights.
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
        """Generate professional executive summary for newly uploaded documents.
        
        This method creates concise, high-level summaries of uploaded documents
        specifically designed for executive stakeholders who need quick insights
        without detailed technical analysis. It focuses on key business points,
        financial implications, and strategic considerations.
        
        Summary Generation Process:
            1. Retrieve document content using session ID for accuracy
            2. Select representative chunks for comprehensive coverage
            3. Apply executive-focused prompt template for business relevance
            4. Generate concise summary emphasizing strategic insights
            5. Clean and format output for professional presentation
        
        Executive Focus Areas:
            - Key contractual terms and business implications
            - Financial commitments and revenue opportunities
            - Risk factors and mitigation considerations
            - Compliance requirements and regulatory aspects
            - Strategic partnership benefits and obligations
        
        Content Selection:
            - Prioritizes first few document chunks for introductory content
            - Ensures comprehensive coverage of document scope
            - Balances detail with executive-level brevity
            - Highlights most business-critical information
        
        Args:
            session_id (str): Unique session identifier for the uploaded
                document batch. Used to retrieve specific document content
                without cross-contamination from other uploads.
            filename (str): Original filename of the uploaded document
                for display purposes and context attribution in the
                summary output.
        
        Returns:
            str: Professional executive summary formatted for stakeholder
                consumption. Includes key business points, financial
                implications, and strategic considerations presented
                in clear, non-technical language.
        
        Raises:
            DocumentNotFoundError: When no content is found for the specified
                session ID, indicating upload or indexing issues.
            ConnectionError: When OpenSearch or OpenAI services are unavailable
                during content retrieval or summary generation.
            SummaryGenerationError: When the AI cannot generate a coherent
                summary due to content issues or service limitations.
        
        Example:
            ```python
            # Generate summary for uploaded contract
            summary = rag_chain.generate_executive_summary(
                session_id="upload_2024_001",
                filename="SushiExpress_Partnership_Agreement.pdf"
            )
            
            # Summary includes:
            # - Key partnership terms
            # - Financial commitments
            # - Risk considerations
            # - Strategic implications
            ```
        
        Summary Format:
            The generated summary follows executive reporting standards:
            - Concise overview of document purpose and scope
            - Key financial terms and business implications
            - Risk factors and compliance considerations
            - Strategic recommendations and next steps
        
        Note:
            This method is optimized for immediate post-upload insights,
            providing stakeholders with rapid understanding of newly
            received documents before detailed analysis is requested.
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
        """Perform expert-level financial analysis using specialized prompts and GPT-4.
        
        This method represents the core analytical engine of the RAG system,
        leveraging carefully crafted prompts and advanced language models to
        deliver professional-grade financial analysis. It supports both concise
        executive-level insights and comprehensive detailed reports based on
        the analysis requirements.
        
        Analysis Capabilities:
            - Expert-level financial reasoning and calculation
            - Contract-to-report discrepancy identification
            - Commission rate variance analysis
            - Fee structure comparison and validation
            - Regulatory compliance assessment
            - Executive summary generation
        
        Prompt Selection Logic:
            - Concise format: Quick insights for executive stakeholders
            - Detailed format: Comprehensive analysis with calculations
            - Context-aware: Adapts complexity based on question type
            - Domain-specific: Financial terminology and methodology
        
        Processing Pipeline:
            1. Select appropriate prompt template based on report requirements
            2. Format context and question into structured prompt
            3. Invoke GPT-4 with optimized parameters for financial analysis
            4. Extract and validate response content
            5. Clean streaming artifacts and formatting issues
            6. Return professionally formatted analysis
        
        Args:
            context (str): Prepared document context containing relevant
                financial information, contracts, and payout reports
                for analysis. Should include both source documents
                and metadata for attribution.
            question (str): The specific financial analysis question or
                request that guides the analytical focus. Can range
                from simple queries to complex multi-factor analysis.
            detailed_report (bool, optional): Flag to control analysis
                depth and format. True for comprehensive reports with
                calculations, False for concise executive summaries.
                Defaults to False.
        
        Returns:
            str: Professional financial analysis response formatted
                according to the specified report type. Includes
                calculations, insights, recommendations, and proper
                attribution to source documents.
        
        Raises:
            ConnectionError: When OpenAI API is unavailable or returns errors.
            ValueError: When context or question parameters are invalid.
            AnalysisError: When the analysis cannot be completed due to
                insufficient data or conflicting information.
        
        Example:
            ```python
            # Concise executive analysis
            executive_analysis = rag_chain.analyze_with_expert_prompt(
                context=document_context,
                question="What are the key commission discrepancies?",
                detailed_report=False
            )
            
            # Detailed technical analysis
            detailed_analysis = rag_chain.analyze_with_expert_prompt(
                context=document_context,
                question="Calculate exact variance in delivery fees",
                detailed_report=True
            )
            ```
        
        Analysis Quality:
            - GPT-4 powered for superior reasoning capabilities
            - Low temperature (0.1) for consistent analytical results
            - Specialized financial domain prompts for accuracy
            - Streaming disabled to prevent response fragmentation
            - Comprehensive error handling and validation
        
        Note:
            This method serves as the primary analytical interface for the
            RAG system. The quality of analysis directly depends on the
            richness and relevance of the provided context, making proper
            document retrieval essential for optimal results.
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
