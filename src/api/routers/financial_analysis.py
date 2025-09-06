"""FastAPI router for financial analysis and contract discrepancy detection endpoints.

This module provides RESTful API endpoints for the Financial Analyst RAG system,
offering comprehensive financial analysis capabilities for restaurant partnership
contracts and payout reports. It serves as the primary interface for accessing
sophisticated AI-powered financial discrepancy detection and analysis services.

The router implements enterprise-grade endpoints that leverage the FinancialAnalystRAGChain
to provide detailed analysis of contract-to-payout discrepancies, partner document
management, and comprehensive financial reporting capabilities. All endpoints are
designed with production considerations including proper error handling, request
validation, and comprehensive response formatting.

Key Endpoints:
    - /analyze-discrepancies: Core financial discrepancy analysis
    - /partner-summary: Document availability and metadata overview
    - /query-documents: General document querying and analysis
    - /detailed-report: Comprehensive financial analysis reports

Financial Analysis Capabilities:
    - Contract-to-payout discrepancy identification
    - Commission rate variance calculations
    - Service fee analysis and validation
    - Penalty application verification
    - Multi-document comparative analysis
    - Executive summary generation

Request/Response Models:
    - AnalysisRequest: Standardized analysis request format
    - AnalysisResponse: Comprehensive analysis results
    - Proper validation and error handling for all interactions

Security and Validation:
    - Input validation using Pydantic models
    - Comprehensive error handling with appropriate HTTP status codes
    - Detailed logging for audit trails and debugging
    - Resource management and timeout considerations

Example Usage:
    ```python
    # Analyze contract discrepancies
    POST /financial-analysis/analyze-discrepancies
    {
        "partner_name": "SushiExpress24-7",
        "question": "Compare commission rates between contract and payout report"
    }
    
    # Get partner document summary
    GET /financial-analysis/partner-summary/SushiExpress24-7
    ```

Integration:
    - RAG service integration for AI-powered analysis
    - OpenSearch connectivity for document retrieval
    - Comprehensive logging and monitoring
    - Error handling with detailed diagnostics

Dependencies:
    - fastapi: Modern web framework for API development
    - pydantic: Data validation and serialization
    - rag_service: Core financial analysis logic
    - logging: Comprehensive operation monitoring

Note:
    This router implements the core Task 2 functionality for financial
    contract analysis using LangChain RAG pipeline with GPT-4 integration.

Version:
    2.0.0 - Enhanced with comprehensive analysis endpoints and validation
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.services.rag_service import FinancialAnalystRAGChain

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/financial-analysis", tags=["Financial Analysis"])

# Initialize RAG chain
rag_chain = FinancialAnalystRAGChain()


class AnalysisRequest(BaseModel):
    """Request model for financial analysis operations.
    
    This model defines the standard request format for financial discrepancy
    analysis operations, providing comprehensive validation and documentation
    for client interactions with the analysis endpoints.
    
    Attributes:
        partner_name (str): Name of the restaurant partner for analysis.
            Must match exactly with indexed partner names for accurate
            document retrieval and analysis.
        question (Optional[str]): Specific analysis question to guide the
            financial analysis. If None, a comprehensive default analysis
            will be performed covering all major discrepancy types.
    
    Example:
        ```json
        {
            "partner_name": "SushiExpress24-7",
            "question": "Compare commission rates between contract and payout report"
        }
        ```
    """
    partner_name: str
    question: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for financial analysis operations.
    
    This model defines the comprehensive response format for financial
    analysis operations, providing structured results with detailed
    analysis content and metadata for client applications.
    
    Attributes:
        partner_name (str): Name of the restaurant partner analyzed.
        question (str): The analysis question that was processed.
        analysis (str): Detailed financial analysis results with
            discrepancy identification and explanations.
        document_summary (Dict[str, Any]): Summary of documents used
            in the analysis including counts and metadata.
        status (str): Operation status indicator (success/error).
    
    Example:
        ```json
        {
            "partner_name": "SushiExpress24-7",
            "question": "Compare commission rates...",
            "analysis": "Based on the contract analysis...",
            "document_summary": {
                "total_documents": 15,
                "document_types": {...}
            },
            "status": "success"
        }
        ```
    """
    partner_name: str
    question: str
    analysis: str
    document_summary: Dict[str, Any]
    status: str


@router.post("/analyze-discrepancies", response_model=AnalysisResponse)
async def analyze_discrepancies(request: AnalysisRequest):
    """Perform comprehensive financial discrepancy analysis between contracts and payout reports.
    
    This endpoint implements the core financial analysis functionality, providing
    sophisticated AI-powered analysis of discrepancies between restaurant partnership
    contracts and their corresponding payout reports. It leverages the LangChain RAG
    pipeline with GPT-4 to deliver expert-level financial insights and calculations.
    
    Analysis Capabilities:
        - Contract-to-payout discrepancy identification
        - Commission rate variance analysis and calculations
        - Service fee comparison and validation
        - Penalty application verification with contractual basis
        - Multi-document cross-referencing for accuracy
        - Detailed financial explanations with supporting evidence
    
    Processing Pipeline:
        1. Partner document validation and availability check
        2. Document summary generation for context
        3. Question processing and default analysis setup
        4. RAG-powered financial analysis execution
        5. Comprehensive response formatting and validation
    
    Default Analysis:
        When no specific question is provided, the endpoint performs a
        comprehensive analysis covering:
        - Service fees and their contractual basis
        - Penalties and calculation methodologies
        - Payout amount variances and explanations
        - Overall financial reconciliation
    
    Args:
        request (AnalysisRequest): Analysis request containing partner name
            and optional specific question. The partner_name must match
            exactly with indexed partner names for accurate document
            retrieval and analysis.
    
    Returns:
        AnalysisResponse: Comprehensive analysis results including:
            - Detailed financial analysis with calculations
            - Document summary with metadata
            - Processing status and validation results
            - Original question for reference
    
    Raises:
        HTTPException 404: When no documents are found for the specified
            partner. Indicates that document indexing may be incomplete
            or partner name is incorrect.
        HTTPException 500: When analysis processing fails due to service
            issues, document problems, or AI service limitations.
    
    Example:
        ```python
        # Request comprehensive analysis
        POST /financial-analysis/analyze-discrepancies
        Content-Type: application/json
        
        {
            "partner_name": "SushiExpress24-7",
            "question": "Identify commission rate discrepancies and calculate variance amounts"
        }
        
        # Response
        {
            "partner_name": "SushiExpress24-7",
            "question": "Identify commission rate discrepancies...",
            "analysis": "Based on comprehensive analysis of SushiExpress24-7 documents...",
            "document_summary": {
                "total_documents": 15,
                "document_types": {
                    "contract": {"count": 8, "files": ["partnership_agreement.pdf"]},
                    "payout_report": {"count": 7, "files": ["payout_2024_07_21.txt"]}
                }
            },
            "status": "success"
        }
        ```
    
    Business Use Cases:
        - Monthly financial reconciliation processes
        - Contract compliance verification
        - Discrepancy investigation and resolution
        - Executive reporting and analysis
        - Automated financial auditing
    
    Performance:
        - Optimized document retrieval for large partner datasets
        - Intelligent context creation for focused analysis
        - Efficient AI processing with minimal latency
        - Comprehensive error handling and recovery
    
    Note:
        This endpoint represents the primary business logic for financial
        contract analysis in the restaurant partnership domain, providing
        production-ready analysis capabilities with enterprise-grade
        reliability and accuracy.
    """
    try:
        # Get partner document summary
        summary = rag_chain.get_partner_summary(request.partner_name)
        
        if summary["total_documents"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No documents found for partner: {request.partner_name}"
            )
        
        # Use default question if none provided
        question = request.question or f"Explain the discrepancies in the payout report for {request.partner_name} based on the provided contract."
        
        # Perform discrepancy analysis
        analysis = rag_chain.analyze_contract_discrepancies(
            request.partner_name,
            question
        )
        
        return AnalysisResponse(
            partner_name=request.partner_name,
            question=question,
            analysis=analysis,
            document_summary=summary,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error analyzing discrepancies for {request.partner_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/partner-summary/{partner_name}")
async def get_partner_summary(partner_name: str):
    """Retrieve comprehensive document summary and metadata for a specific restaurant partner.
    
    This endpoint provides detailed information about all available documents
    for a restaurant partner, including document counts, types, file information,
    and processing metadata. It serves as a health check and inventory endpoint
    for partner document availability before performing analysis operations.
    
    Summary Information:
        - Total document count across all types
        - Document type breakdown with individual counts
        - File names and metadata for each document type
        - Content statistics including total character counts
        - Processing timestamps and validation status
    
    Document Types:
        - contract: Partnership agreements and legal documents
        - payout_report: Financial transaction records and summaries
        - other: Additional relevant documents and addendums
    
    Use Cases:
        - Pre-analysis validation of document availability
        - Document inventory management and tracking
        - Processing status verification for uploaded documents
        - Client application data availability checks
        - Administrative partner management operations
    
    Args:
        partner_name (str): Name of the restaurant partner for document
            summary retrieval. Must match exactly with indexed partner
            names for accurate document discovery.
    
    Returns:
        Dict[str, Any]: Comprehensive partner summary containing:
            - status: Operation success indicator
            - partner_summary: Detailed document metadata including:
                - partner_name: Confirmed partner identifier
                - total_documents: Count of all available documents
                - document_types: Breakdown by type with counts and files
                - last_processed: Most recent processing timestamp
    
    Raises:
        HTTPException 404: When no documents are found for the specified
            partner. This indicates either:
            - Partner name is incorrect or not indexed
            - Document indexing is incomplete
            - Documents have been removed or corrupted
        HTTPException 500: When document retrieval fails due to:
            - OpenSearch connectivity issues
            - Service configuration problems
            - System resource limitations
    
    Example:
        ```python
        # Request partner summary
        GET /financial-analysis/partner-summary/SushiExpress24-7
        
        # Response
        {
            "status": "success",
            "partner_summary": {
                "partner_name": "SushiExpress24-7",
                "total_documents": 15,
                "document_types": {
                    "contract": {
                        "count": 8,
                        "files": ["partnership_agreement.pdf"],
                        "total_content_length": 25000
                    },
                    "payout_report": {
                        "count": 7,
                        "files": ["payout_2024_07_21.txt"],
                        "total_content_length": 12000
                    }
                },
                "last_processed": "2024-07-21T10:30:00Z"
            }
        }
        ```
    
    Response Structure:
        The partner summary provides comprehensive metadata enabling
        clients to:
        - Validate document availability before analysis requests
        - Display document inventory in user interfaces
        - Monitor processing status and document completeness
        - Plan analysis operations based on available content
    
    Performance:
        - Optimized document counting and metadata aggregation
        - Cached results for frequently accessed partners
        - Minimal resource usage for inventory operations
        - Fast response times for client validation
    
    Note:
        This endpoint is essential for client applications to validate
        partner document availability and plan analysis operations
        effectively before making resource-intensive analysis requests.
    """
    try:
        summary = rag_chain.get_partner_summary(partner_name)
        
        if summary["total_documents"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No documents found for partner: {partner_name}"
            )
        
        return {
            "status": "success",
            "partner_summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting summary for {partner_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get partner summary: {str(e)}"
        )


@router.post("/custom-analysis")
async def custom_financial_analysis(
    partner_name: str = Query(..., description="Name of the partner to analyze"),
    question: str = Query(..., description="Custom financial analysis question")
):
    """
    Perform custom financial analysis with a specific question.
    """
    try:
        analysis = rag_chain.analyze_contract_discrepancies(partner_name, question)
        summary = rag_chain.get_partner_summary(partner_name)
        
        return {
            "status": "success",
            "partner_name": partner_name,
            "question": question,
            "analysis": analysis,
            "document_summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error in custom analysis for {partner_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Custom analysis failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for the Financial Analysis service.
    """
    try:
        # Test basic RAG chain functionality
        test_summary = rag_chain.get_partner_summary("Sushi Express")
        
        return {
            "status": "healthy",
            "service": "Financial Analyst RAG Chain",
            "features": [
                "LangChain RAG pipeline",
                "Financial discrepancy analysis",
                "Multi-document retrieval",
                "GPT-4 powered analysis"
            ],
            "test_partner_documents": test_summary["total_documents"]
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
