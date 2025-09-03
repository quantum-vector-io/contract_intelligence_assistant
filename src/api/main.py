"""
FastAPI main application for Contract Intelligence Assistant.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import logging

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.core.config import settings
from src.api.routers import opensearch, documents, financial_analysis

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered financial analysis for restaurant partnership payments",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(opensearch.router)
app.include_router(documents.router)
app.include_router(financial_analysis.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

# Task 3: Core /analyze endpoint for orchestrating indexing + querying
@app.post("/analyze")
async def analyze_documents(
    contract_file: UploadFile = File(..., description="Partnership contract document"),
    payout_file: UploadFile = File(..., description="Payout report document"),
    question: str = Form(..., description="Question to analyze")
):
    """
    Task 3: Single endpoint to orchestrate the entire analysis process.
    
    This endpoint:
    1. Accepts multiple file uploads (contract + payout report)
    2. Indexes both documents with proper metadata
    3. Uses the RAG chain to answer the user's question
    4. Returns the AI's response
    """
    from src.services.document_indexing_service import DocumentIndexingService
    from src.services.rag_service import FinancialAnalystRAGChain
    import tempfile
    import uuid
    
    # Generate unique partner ID for this analysis session
    session_id = str(uuid.uuid4())[:8]
    partner_name = f"Analysis_Session_{session_id}"
    
    try:
        # Initialize services
        indexing_service = DocumentIndexingService()
        rag_chain = FinancialAnalystRAGChain()
        
        # Track processing results
        results = {
            "session_id": session_id,
            "contract_indexed": False,
            "payout_indexed": False,
            "analysis_successful": False,
            "answer": "",
            "error": None
        }
        
        # Process contract file
        contract_temp_path = None
        try:
            # Create temporary file for contract
            with tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=os.path.splitext(contract_file.filename or ".pdf")[1]
            ) as temp_file:
                content = await contract_file.read()
                temp_file.write(content)
                contract_temp_path = temp_file.name
            
            # Index contract with metadata
            contract_metadata = {
                "partner_name": partner_name,
                "document_type": "contract",
                "partner_id": session_id,
                "original_filename": contract_file.filename,
                "session_id": session_id
            }
            
            contract_result = indexing_service.index_file(contract_temp_path, contract_metadata)
            results["contract_indexed"] = contract_result.get("status") == "success"
            
        finally:
            # Clean up contract temp file
            if contract_temp_path and os.path.exists(contract_temp_path):
                os.unlink(contract_temp_path)
        
        # Process payout file
        payout_temp_path = None
        try:
            # Create temporary file for payout report
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(payout_file.filename or ".pdf")[1]
            ) as temp_file:
                content = await payout_file.read()
                temp_file.write(content)
                payout_temp_path = temp_file.name
            
            # Index payout report with metadata
            payout_metadata = {
                "partner_name": partner_name,
                "document_type": "payout_report",
                "partner_id": session_id,
                "original_filename": payout_file.filename,
                "session_id": session_id
            }
            
            payout_result = indexing_service.index_file(payout_temp_path, payout_metadata)
            results["payout_indexed"] = payout_result.get("status") == "success"
            
        finally:
            # Clean up payout temp file
            if payout_temp_path and os.path.exists(payout_temp_path):
                os.unlink(payout_temp_path)
        
        # Perform RAG analysis if both documents were indexed successfully
        if results["contract_indexed"] and results["payout_indexed"]:
            try:
                # Use the RAG chain to analyze the documents
                analysis_result = rag_chain.analyze_contract_discrepancies(partner_name, question)
                results["analysis_successful"] = True
                results["answer"] = analysis_result
                
            except Exception as e:
                results["error"] = f"Analysis failed: {str(e)}"
                logger.error(f"RAG analysis failed: {e}")
        else:
            results["error"] = "Failed to index one or both documents"
        
        # Return comprehensive results
        return {
            "status": "success" if results["analysis_successful"] else "error",
            "session_id": session_id,
            "question": question,
            "contract_file": contract_file.filename,
            "payout_file": payout_file.filename,
            "contract_indexed": results["contract_indexed"],
            "payout_indexed": results["payout_indexed"],
            "analysis_successful": results["analysis_successful"],
            "answer": results["answer"] if results["analysis_successful"] else None,
            "error": results["error"]
        }
        
    except Exception as e:
        logger.error(f"Analysis endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/query")
async def query_database(request: dict):
    """
    Database-only query endpoint for searching existing documents.
    
    This endpoint:
    1. Accepts a question in JSON format
    2. Uses the RAG chain to search existing indexed documents
    3. Returns the AI's response without indexing new documents
    """
    try:
        question = request.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Use RAG service to query existing documents
        from src.services.rag_service import FinancialAnalystRAGChain
        rag_chain = FinancialAnalystRAGChain()
        
        answer = rag_chain.query_all_documents(question)
        
        return {
            "status": "success",
            "question": question,
            "answer": answer
        }
        
    except Exception as e:
        logger.error(f"Query endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
