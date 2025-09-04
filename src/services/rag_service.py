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
        
        # Financial analyst master prompt as required by Task 2
        self.financial_analyst_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a senior financial analyst specializing in restaurant partnership agreements and payout reconciliation. Your role is to analyze contracts and financial reports to identify discrepancies, explain variances, and provide detailed financial insights.

ANALYSIS FRAMEWORK:
1. CONTRACT TERMS: Focus on commission rates, fees, penalties, and payment structures
2. FINANCIAL RECONCILIATION: Compare actual payouts against contractual expectations
3. DISCREPANCY IDENTIFICATION: Highlight differences between contracted terms and actual payments
4. ROOT CAUSE ANALYSIS: Explain why discrepancies occurred (service fees, penalties, bonuses, etc.)

CONTEXT DOCUMENTS:
{context}

ANALYSIS REQUEST:
{question}

FINANCIAL ANALYSIS RESPONSE:
Provide a comprehensive analysis that includes:
1. **Contract Summary**: Key financial terms from the partnership agreement
2. **Payout Analysis**: Breakdown of the actual payout amounts and calculations
3. **Discrepancy Identification**: Specific differences between contract terms and actual payouts
4. **Financial Explanation**: Detailed reasoning for each discrepancy (cite specific contract clauses)
5. **Recommendations**: Suggested actions or clarifications needed

Ensure your analysis is:
- Precise with numbers and percentages
- Cites specific contract clauses or payout line items
- Explains the financial impact of each discrepancy
- Professional and analytical in tone

ANALYSIS:"""
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
        
        # Simple relevance scoring based on keyword overlap
        # In production, this would use vector similarity search
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
    
    def analyze_contract_discrepancies(self, partner_name: str, specific_question: Optional[str] = None) -> str:
        """
        Analyze discrepancies between a partner's contract and payout reports.
        
        Args:
            partner_name: Name of the partner to analyze
            specific_question: Optional specific question to focus the analysis
            
        Returns:
            Detailed financial analysis explaining discrepancies
        """
        # Default question if none provided
        if not specific_question:
            specific_question = f"Explain the discrepancies in the payout report for {partner_name} based on the provided contract. Identify the service fees and penalties that cause differences in the payout amounts."
        
        try:
            # Create retrieval context
            context = self.create_retrieval_context(partner_name, specific_question)
            
            # Generate analysis using the financial analyst prompt
            response = self.llm.invoke(
                self.financial_analyst_prompt.format(
                    context=context,
                    question=specific_question
                )
            )
            
            analysis = response.content if hasattr(response, 'content') else str(response)
            
            # Clean up any potential streaming artifacts
            analysis = self._clean_response_text(analysis)
            
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
            
            logger.info(f"Generated database query analysis for: {question}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error querying all documents: {e}")
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
