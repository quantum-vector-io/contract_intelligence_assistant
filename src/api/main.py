"""
FastAPI main application for Contract Intelligence Assistant.

This module initializes and configures the FastAPI web application that serves
as the backend for the Contract Intelligence Assistant platform. It provides
REST endpoints for document processing, financial analysis, and system health
monitoring through modular routers.

The application includes CORS middleware for cross-origin requests and
conditional API documentation based on debug settings.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import logging

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.core.config import settings
from src.api.routers import opensearch, documents, financial_analysis, dashboard

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
app.include_router(dashboard.router)

@app.get("/")
async def root():
    """Return basic application information and status.
    
    Provides the application name, version, and current running status
    for health monitoring and service identification purposes.
    
    Returns:
        dict: Application metadata containing name, version, and status.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Perform application health check.
    
    Returns the current health status of the application including
    service name and version information for monitoring systems.
    
    Returns:
        dict: Health status information with service details.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

async def generate_document_summary(
    contract_file: UploadFile = None,
    payout_file: UploadFile = None,
    filename: str = None
):
    """Generate an executive summary for uploaded document(s).
    
    Processes uploaded contract or payout files through the document indexing
    and RAG services to generate intelligent summaries. Creates a temporary
    session for document processing and analysis.
    
    Args:
        contract_file (UploadFile, optional): Contract document to analyze.
        payout_file (UploadFile, optional): Payout report to analyze.
        filename (str, optional): Custom filename for the document.
        
    Returns:
        dict: Summary results or error information.
        
    Raises:
        Exception: When document processing or analysis fails.
    """
    from src.services.document_indexing_service import DocumentIndexingService
    from src.services.rag_service import FinancialAnalystRAGChain
    import tempfile
    import uuid
    
    session_id = str(uuid.uuid4())[:8]
    
    try:
        # Initialize services
        indexing_service = DocumentIndexingService()
        rag_chain = FinancialAnalystRAGChain()
        
        # Process the uploaded file
        temp_path = None
        file_to_process = contract_file if contract_file else payout_file
        
        if not file_to_process:
            return {"status": "error", "error": "No file provided"}
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(file_to_process.filename or ".pdf")[1]
            ) as temp_file:
                content = await file_to_process.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Index document with metadata
            metadata = {
                "partner_name": f"Summary_Session_{session_id}",
                "document_type": "contract" if contract_file else "payout_report",
                "partner_id": session_id,
                "original_filename": file_to_process.filename,
                "session_id": session_id
            }
            
            result = indexing_service.index_file(temp_path, metadata)
            
            if result.get("status") == "success":
                # Refresh index
                indexing_service.opensearch_service.client.indices.refresh(index="financial_documents")
                
                # Generate summary
                import time
                time.sleep(1)
                
                summary = rag_chain.generate_executive_summary(session_id, filename or file_to_process.filename)
                
                return {
                    "status": "success",
                    "summary": summary,
                    "filename": filename or file_to_process.filename,
                    "session_id": session_id
                }
            else:
                return {"status": "error", "error": "Failed to index document"}
                
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return {"status": "error", "error": str(e)}

# Task 3: Core /analyze endpoint for orchestrating indexing + querying
@app.post("/analyze")
async def analyze_documents(
    contract_file: UploadFile = File(None, description="Partnership contract document"),
    payout_file: UploadFile = File(None, description="Payout report document"),
    question: str = Form(None, description="Question to analyze"),
    query_database: str = Form("false", description="Whether to query existing database"),
    action: str = Form("analyze", description="Action to perform: 'analyze' or 'summary'"),
    filename: str = Form(None, description="Original filename for summary generation"),
    detailed_report: str = Form("false", description="Whether to generate detailed report format")
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
    
    # Convert parameters to booleans
    should_query_database = query_database.lower() == "true"
    is_detailed_report = detailed_report.lower() == "true"
    logger.info(f"DEBUG: query_database flag: {should_query_database}")
    logger.info(f"DEBUG: action: {action}")
    logger.info(f"DEBUG: detailed_report: {is_detailed_report}")
    
    # Handle summary generation action
    if action == "summary":
        if not filename:
            raise HTTPException(status_code=400, detail="Filename required for summary generation")
        
        # For summary, we need at least one real file
        has_real_contract = contract_file is not None and contract_file.filename != "dummy_contract.txt"
        has_real_payout = payout_file is not None and payout_file.filename != "dummy_payout.txt"
        
        if not has_real_contract and not has_real_payout:
            raise HTTPException(status_code=400, detail="No valid files provided for summary generation")
        
        return await generate_document_summary(
            contract_file if has_real_contract else None,
            payout_file if has_real_payout else None,
            filename
        )
    
    # For analyze action, question is required
    if not question:
        raise HTTPException(status_code=400, detail="Question is required for analysis")
    
    # Generate unique partner ID for this analysis session
    session_id = str(uuid.uuid4())[:8]
    
    # Extract partner name from filenames
    def extract_partner_name(filename):
        """Extract partner name from filename."""
        logger.info(f"DEBUG: Extracting partner name from filename: {filename}")
        if not filename:
            logger.info("DEBUG: No filename provided")
            return None
        filename_lower = filename.lower()
        logger.info(f"DEBUG: Filename lowercase: {filename_lower}")
        if "sushiexpress" in filename_lower or "sushi" in filename_lower:
            logger.info("DEBUG: Detected Sushi Express")
            return "Sushi Express 24/7"
        elif "goldenfork" in filename_lower:
            logger.info("DEBUG: Detected Golden Fork")
            return "The Golden Fork Pizzeria"
        elif "schnitzelhaus" in filename_lower:
            logger.info("DEBUG: Detected SchnitzelHaus")
            return "SchnitzelHaus"
        elif "urbanspice" in filename_lower:
            logger.info("DEBUG: Detected Urban Spice")
            return "Urban Spice Group"
        logger.info("DEBUG: No partner detected")
        return None
    
    def get_partner_id(partner_name):
        """Get partner ID from partner name."""
        if partner_name == "Sushi Express 24/7":
            return "sushi_express_247"
        elif partner_name == "The Golden Fork Pizzeria":
            return "golden_fork_pizzeria"
        elif partner_name == "SchnitzelHaus":
            return "schnitzel_haus"
        elif partner_name == "Urban Spice Group":
            return "urban_spice_group"
        return session_id  # Fallback to session ID
    
    # Try to extract partner name from either file
    partner_name = None
    if contract_file and contract_file.filename:
        logger.info(f"DEBUG: Trying to extract partner from contract file: {contract_file.filename}")
        partner_name = extract_partner_name(contract_file.filename)
    if not partner_name and payout_file and payout_file.filename:
        logger.info(f"DEBUG: Trying to extract partner from payout file: {payout_file.filename}")
        partner_name = extract_partner_name(payout_file.filename)
    
    logger.info(f"DEBUG: Final partner_name: {partner_name}")
    
    # Fallback to session-based name if no partner detected
    if not partner_name:
        partner_name = f"Analysis_Session_{session_id}"
        logger.info(f"DEBUG: Using fallback partner name: {partner_name}")
    
    partner_id = get_partner_id(partner_name)
    logger.info(f"DEBUG: Final partner_id: {partner_id}")
    
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
        
        # Validate that we have at least one real file (not dummy)
        has_real_contract = contract_file is not None and contract_file.filename != "dummy_contract.txt"
        has_real_payout = payout_file is not None and payout_file.filename != "dummy_payout.txt"
        
        if not has_real_contract and not has_real_payout:
            results["error"] = "No valid files provided for analysis"
            results["analysis_successful"] = False
            return results
        
        # Process contract file
        contract_temp_path = None
        if has_real_contract:
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
                    "partner_id": partner_id,
                    "original_filename": contract_file.filename,
                    "session_id": session_id
                }
                
                contract_result = indexing_service.index_file(contract_temp_path, contract_metadata)
                results["contract_indexed"] = contract_result.get("status") == "success"
                
            except Exception as e:
                logger.error(f"Error processing contract file: {e}")
                results["contract_indexed"] = False
            finally:
                # Clean up contract temp file
                if contract_temp_path and os.path.exists(contract_temp_path):
                    os.unlink(contract_temp_path)
        
        # Process payout file
        payout_temp_path = None
        if has_real_payout:
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
                    "partner_id": partner_id,
                    "original_filename": payout_file.filename,
                    "session_id": session_id
                }
                
                payout_result = indexing_service.index_file(payout_temp_path, payout_metadata)
                results["payout_indexed"] = payout_result.get("status") == "success"
                
            except Exception as e:
                results["error"] = f"Failed to process payout file: {str(e)}"
                logger.error(f"Payout file processing failed: {e}")
                
            finally:
                # Clean up payout temp file
                if payout_temp_path and os.path.exists(payout_temp_path):
                    os.unlink(payout_temp_path)
        
        # Perform RAG analysis if at least one document was indexed successfully
        if results["contract_indexed"] or results["payout_indexed"]:
            try:
                # Refresh the index to ensure documents are immediately searchable
                indexing_service.opensearch_service.client.indices.refresh(index="financial_documents")
                logger.info("DEBUG: Index refreshed for immediate search")
                
                # Add a small delay to ensure indexing is complete
                import time
                time.sleep(1)
                logger.info("DEBUG: Starting RAG analysis")
                
                # Choose analysis approach based on files and database query flag
                if results["contract_indexed"] and results["payout_indexed"]:
                    # Both documents uploaded - always use contract discrepancy analysis
                    logger.info(f"DEBUG: Analyzing discrepancies for partner: {partner_name}")
                    analysis_result = rag_chain.analyze_contract_discrepancies(partner_name, question, is_detailed_report)
                elif should_query_database:
                    # Single document with database query enabled - search across all documents
                    logger.info(f"DEBUG: Using database query analysis (query_database=true)")
                    analysis_result = rag_chain.query_all_documents(question)
                else:
                    # Single document with database query disabled - only analyze uploaded document
                    logger.info(f"DEBUG: Using session-specific query for uploaded document only: {session_id}")
                    analysis_result = rag_chain.query_session_documents(session_id, question, detailed_report=is_detailed_report)
                
                results["analysis_successful"] = True
                results["answer"] = analysis_result
                
            except Exception as e:
                results["error"] = f"Analysis failed: {str(e)}"
                logger.error(f"RAG analysis failed: {e}")
        else:
            results["error"] = "Failed to index any documents"
        
        # Return comprehensive results
        return {
            "status": "success" if results["analysis_successful"] else "error",
            "session_id": session_id,
            "question": question,
            "contract_file": contract_file.filename if contract_file else None,
            "payout_file": payout_file.filename if payout_file else None,
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
        
        # Check if there are any documents in the database first
        from src.services.opensearch_service import OpenSearchService
        opensearch_service = OpenSearchService()
        
        # Get document count
        count_response = opensearch_service.client.count(
            index=opensearch_service.index_name
        )
        doc_count = count_response.get("count", 0)
        
        if doc_count == 0:
            return {
                "status": "no_documents",
                "question": question,
                "answer": "🔍 No documents found in the database. Please upload some contract documents first to use the database query feature.",
                "suggestion": "Upload PDF contracts or payout reports to build your document database, then try your query again."
            }
        
        answer = rag_chain.query_all_documents(question)
        
        return {
            "status": "success",
            "question": question,
            "answer": answer,
            "documents_found": doc_count
        }
        
    except Exception as e:
        logger.error(f"Query endpoint failed: {e}")
        # Provide more specific error information
        if "index_not_found_exception" in str(e).lower():
            return {
                "status": "no_index",
                "question": question,
                "answer": "🔍 Document database is not initialized. Please upload some documents first to create the search index.",
                "suggestion": "Upload PDF contracts or payout reports to initialize the database, then try your query again."
            }
        else:
            raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
