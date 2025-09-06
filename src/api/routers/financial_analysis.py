"""FastAPI router for financial analysis and contract discrepancy detection.

Provides RESTful API endpoints for analyzing restaurant partnership contracts
and payout reports using the FinancialAnalystRAGChain.

Key Endpoints:
    - /analyze-discrepancies: Financial discrepancy analysis
    - /partner-summary: Document overview and metadata
    - /query-documents: General document querying
    - /detailed-report: Comprehensive analysis reports

Example:
    ```python
    # POST /analyze-discrepancies
    request = {"partner_name": "Restaurant", "analysis_type": "full"}
    ```
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
    
    Attributes:
        partner_name (str): Restaurant partner name for analysis.
        question (Optional[str]): Specific analysis question or None for default.
    """
    partner_name: str
    question: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for financial analysis operations.
    
    Attributes:
        partner_name (str): Restaurant partner analyzed.
        question (str): Analysis question processed.
        analysis (str): Financial analysis results.
        document_summary (Dict[str, Any]): Documents used in analysis.
        status (str): Operation status (success/error).
    """
    partner_name: str
    question: str
    analysis: str
    document_summary: Dict[str, Any]
    status: str


@router.post("/analyze-discrepancies", response_model=AnalysisResponse)
async def analyze_discrepancies(request: AnalysisRequest):
    """Analyze financial discrepancies between contracts and payout reports.
    
    Args:
        request: Analysis request with partner name and optional question.
        
    Returns:
        Analysis response with results and document summary.
        
    Raises:
        HTTPException: If analysis fails or partner not found.
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
    """Get document summary for a restaurant partner.
    
    Args:
        partner_name (str): Restaurant partner name.
        
    Returns:
        Dict with document counts, types, and metadata.
        
    Raises:
        HTTPException: If partner not found or service error.
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
