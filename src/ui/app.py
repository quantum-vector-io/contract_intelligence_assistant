"""Advanced Streamlit interface for Contract Intelligence Assistant platform.

This module provides a comprehensive web-based user interface for the Contract
Intelligence Assistant, enabling restaurant partners and financial analysts to
interact with sophisticated AI-powered contract analysis and discrepancy detection
capabilities. The interface is built with Streamlit for rapid deployment and
intuitive user experience.

The application serves as the primary client interface for the Financial Analyst RAG
system, providing seamless access to document upload, processing, analysis, and
reporting capabilities. It implements modern UI patterns with responsive design,
real-time status monitoring, and comprehensive error handling for production use.

Key Features:
    - Document upload and processing interface for contracts and payout reports
    - Real-time API health monitoring and status indicators
    - Interactive query interface with natural language processing
    - Automatic executive summary generation for uploaded documents
    - Comprehensive financial analysis with detailed and concise reporting modes
    - Session state management for user experience continuity
    - Responsive design with multi-column layouts for optimal usability

User Interface Components:
    - File upload widgets for PDF and text document processing
    - Query interface with customizable analysis parameters
    - Real-time status monitoring and health checks
    - Interactive results display with formatted analysis output
    - Configuration panels for user preferences and options
    - Error handling with user-friendly messaging

Document Processing Workflow:
    1. Document upload validation and format checking
    2. Automatic processing and indexing via API calls
    3. Optional executive summary generation
    4. Document availability validation for analysis
    5. Interactive query processing with real-time feedback

Analysis Capabilities:
    - Contract-to-payout discrepancy analysis
    - Commission rate variance calculations
    - Service fee validation and explanations
    - Multi-document comparative analysis
    - Executive summary generation
    - Detailed financial reporting with calculations

Session Management:
    - Upload tracking and document session management
    - Query history and context preservation
    - User preference persistence across sessions
    - Error state handling and recovery

Technical Features:
    - Streamlit framework for rapid web application development
    - RESTful API integration for backend service communication
    - Real-time health monitoring and status reporting
    - Responsive layout design for desktop and mobile compatibility
    - Session state management for user experience optimization

Example Usage:
    The application provides an intuitive workflow:
    1. Upload restaurant partnership contract (PDF/TXT)
    2. Upload corresponding payout report (PDF/TXT)
    3. Ask natural language questions about discrepancies
    4. Receive detailed AI-powered financial analysis
    5. Generate executive summaries for stakeholder reporting

Integration Points:
    - FastAPI backend for document processing and analysis
    - Financial Analyst RAG system for AI-powered insights
    - OpenSearch for document storage and retrieval
    - File upload and session management systems

Dependencies:
    - streamlit: Modern web application framework
    - requests: HTTP client for API communication
    - config: Application configuration management
    - logging: Comprehensive operation monitoring

Note:
    This interface is designed for production use with enterprise-grade
    error handling, security considerations, and user experience optimization.
    It serves as the primary client interface for the Contract Intelligence
    Assistant platform.

Version:
    2.0.0 - Enhanced with comprehensive analysis features and improved UX
"""
import streamlit as st
import requests
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from src.core.config import settings
except ImportError:
    # Fallback if config not available
    class Settings:
        api_port = 8000
        app_name = "Contract Intelligence Assistant"
    settings = Settings()

# Page configuration
st.set_page_config(
    page_title="Contract Intelligence Assistant",
    page_icon="💼",
    layout="wide"
)

# Main title
st.title("💼 Contract Intelligence Assistant")
st.markdown("*AI-powered financial analysis for restaurant partnership payments*")

# API Status check
st.sidebar.markdown("### 🔧 System Status")
try:
    response = requests.get(f"http://localhost:{settings.api_port}/health", timeout=2)
    if response.status_code == 200:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Error")
except:
    st.sidebar.error("❌ API Not Available")
    st.sidebar.info("Start API: python src/api/main.py")

# Query Options Panel
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Query Options")

# Initialize session state variables
if 'summary_on_upload' not in st.session_state:
    st.session_state.summary_on_upload = True

if 'last_question' not in st.session_state:
    st.session_state.last_question = None

if 'last_context' not in st.session_state:
    st.session_state.last_context = None

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

if 'last_session_id' not in st.session_state:
    st.session_state.last_session_id = None

if 'generate_detailed_report' not in st.session_state:
    st.session_state.generate_detailed_report = False

# Auto-summary checkbox
st.session_state.summary_on_upload = st.sidebar.checkbox(
    'Auto-generate summary on file upload', 
    value=st.session_state.summary_on_upload,
    key='summary_checkbox',
    help="When enabled, automatically generates an executive summary for each uploaded file"
)

# Main content
st.markdown("## 📄 Upload Documents")

col1, col2 = st.columns(2)

with col1:
    contract_file = st.file_uploader(
        "Partnership Contract", 
        type=['pdf', 'txt'],
        help="Upload your restaurant partnership agreement"
    )

with col2:
    payout_file = st.file_uploader(
        "Payout Report",
        type=['pdf', 'txt'], 
        help="Upload your latest payout statement"
    )

# Query section
st.markdown("## 💬 Ask Questions")

# Add option for database queries
col_q1, col_q2 = st.columns([3, 1])
with col_q1:
    query = st.text_area(
        "Your Question",
        placeholder="Example: Why is my commission different from the contract?",
        height=100
    )
with col_q2:
    st.markdown("**Query Options:**")
    query_database = st.checkbox(
        "Query existing database",
        help="Search across all previously uploaded documents"
    )

# Ask button - right below the input field
col_ask1, col_ask2 = st.columns([2, 1])
with col_ask1:
    ask_button_clicked = st.button("🔍 Ask", type="primary", help="Ask your question and get an analysis")
with col_ask2:
    st.write("")  # Empty space

# Manual action buttons
st.markdown("---")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    # Generate Summary button - enabled when files are uploaded
    has_files = contract_file or payout_file
    generate_summary_disabled = not has_files
    
    if st.button(
        "📋 Generate Summary", 
        disabled=generate_summary_disabled,
        help="Generate executive summaries for uploaded documents"
    ):
        if has_files:
            # Store uploaded files info for summary generation
            summary_files = []
            if contract_file:
                summary_files.append(('contract', contract_file))
            if payout_file:
                summary_files.append(('payout', payout_file))
            st.session_state.generate_summary_requested = summary_files

with col_btn2:
    # Generate Detailed Report button - always enabled (can work with uploaded files or database)
    detailed_report_disabled = False  # Always enabled
    
    if st.button(
        "📊 Generate Detailed Report", 
        disabled=detailed_report_disabled,
        help="Generate a comprehensive analysis report (works with uploaded files or database documents)"
    ):
        # Always set the flag when button is clicked, regardless of previous questions
        st.session_state.generate_detailed_report = True
        st.success("🔄 Detailed report requested! Processing...")

st.markdown("---")

# Track file uploads and auto-generate summaries if enabled
current_files = []
if contract_file:
    current_files.append(('contract', contract_file))
if payout_file:
    current_files.append(('payout', payout_file))

# Check if files have changed and auto-summary is enabled
if current_files != st.session_state.uploaded_files and st.session_state.summary_on_upload and current_files:
    st.session_state.uploaded_files = current_files
    st.session_state.auto_generate_summary = True

# Handle manual summary generation
if 'generate_summary_requested' in st.session_state and st.session_state.generate_summary_requested:
    current_files = st.session_state.generate_summary_requested
    st.session_state.generate_summary_requested = None
    st.session_state.manual_generate_summary = True

# Generate summaries (auto or manual)
if ('auto_generate_summary' in st.session_state and st.session_state.auto_generate_summary) or \
   ('manual_generate_summary' in st.session_state and st.session_state.manual_generate_summary):
    
    if 'auto_generate_summary' in st.session_state:
        st.session_state.auto_generate_summary = False
        st.markdown("### 🔄 Auto-Generating Document Summaries...")
    else:
        st.session_state.manual_generate_summary = False
        st.markdown("### 📋 Generating Document Summaries...")
    
    # Generate summaries for each file
    for file_type, file_obj in current_files:
        if file_obj:
            with st.spinner(f"🔍 Analyzing {file_obj.name}..."):
                try:
                    # Upload file and get summary
                    files = {}
                    data = {
                        'action': 'summary',
                        'filename': file_obj.name
                    }
                    
                    if file_type == 'contract':
                        files['contract_file'] = (file_obj.name, file_obj.getvalue(), file_obj.type)
                        files['payout_file'] = ('dummy_payout.txt', b'No payout report provided.', 'text/plain')
                    else:
                        files['payout_file'] = (file_obj.name, file_obj.getvalue(), file_obj.type)
                        files['contract_file'] = ('dummy_contract.txt', b'No contract provided.', 'text/plain')
                    
                    response = requests.post(
                        f"http://localhost:{settings.api_port}/analyze",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("status") == "success" and result.get("summary"):
                            # Display the summary
                            def escape_latex(text):
                                text = text.replace('$', '\\$')
                                text = text.replace('_', '\\_')
                                text = text.replace('^', '\\^')
                                text = text.replace('#', '\\#')
                                return text
                            
                            escaped_summary = escape_latex(result.get("summary"))
                            st.markdown(escaped_summary)
                        else:
                            st.error(f"❌ Failed to generate summary for {file_obj.name}")
                    else:
                        st.error(f"❌ Server error generating summary for {file_obj.name}")
                        
                except Exception as e:
                    st.error(f"❌ Error generating summary for {file_obj.name}: {str(e)}")
    
    st.markdown("---")

# Handle detailed report generation
if 'generate_detailed_report' in st.session_state and st.session_state.generate_detailed_report:
    st.session_state.generate_detailed_report = False
    
    st.markdown("### 📊 Generating Detailed Analysis Report...")
    
    with st.spinner("🔄 Creating comprehensive report..."):
        try:
            # Determine what to analyze
            has_current_files = contract_file or payout_file
            has_previous_question = st.session_state.last_question
            
            if has_current_files:
                # Use current uploaded files
                question_to_use = st.session_state.last_question if has_previous_question else "Provide a comprehensive analysis of this document, including key financial terms, potential risks, and recommendations."
                
                data = {
                    'question': question_to_use,
                    'query_database': str(query_database).lower(),
                    'detailed_report': 'true'
                }
                
                # Prepare current files
                files = {}
                if contract_file:
                    files['contract_file'] = (contract_file.name, contract_file.getvalue(), contract_file.type)
                else:
                    files['contract_file'] = ('dummy_contract.txt', b'No contract provided.', 'text/plain')
                
                if payout_file:
                    files['payout_file'] = (payout_file.name, payout_file.getvalue(), payout_file.type)
                else:
                    files['payout_file'] = ('dummy_payout.txt', b'No payout provided.', 'text/plain')
                    
            elif has_previous_question and st.session_state.last_context:
                # Use previous question and context
                data = {
                    'question': st.session_state.last_question,
                    'query_database': str(st.session_state.last_context.get('query_database', False)).lower(),
                    'detailed_report': 'true'
                }
                
                # Prepare dummy files (will use database query)
                files = {
                    'contract_file': ('dummy_contract.txt', b'No contract provided.', 'text/plain'),
                    'payout_file': ('dummy_payout.txt', b'No payout provided.', 'text/plain')
                }
                
            else:
                # Default database query for comprehensive analysis
                data = {
                    'question': "Provide a comprehensive analysis of all available documents, including key financial terms, potential risks, and recommendations across all partnerships.",
                    'query_database': 'true',
                    'detailed_report': 'true'
                }
                
                files = {
                    'contract_file': ('dummy_contract.txt', b'No contract provided.', 'text/plain'),
                    'payout_file': ('dummy_payout.txt', b'No payout provided.', 'text/plain')
                }
            
            response = requests.post(
                f"http://localhost:{settings.api_port}/analyze",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success" and result.get("analysis_successful"):
                    # Display the detailed report
                    def escape_latex(text):
                        text = text.replace('$', '\\$')
                        text = text.replace('_', '\\_')
                        text = text.replace('^', '\\^')
                        text = text.replace('#', '\\#')
                        return text
                    
                    answer = result.get("answer", "No detailed report generated")
                    escaped_answer = escape_latex(answer)
                    st.markdown("### 📋 Detailed Analysis Report")
                    st.markdown(escaped_answer)
                else:
                    st.error("❌ Failed to generate detailed report")
                    if result.get("error"):
                        st.error(f"Error details: {result.get('error')}")
            else:
                st.error(f"❌ Server error generating detailed report ({response.status_code})")
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"Details: {error_detail}")
                except:
                    st.error("Failed to get error details from server")
                
        except Exception as e:
            st.error(f"❌ Error generating detailed report: {str(e)}")
    
    st.markdown("---")

if ask_button_clicked:
    # Check if we have files, database query option, and a question
    has_files = contract_file or payout_file
    
    if (has_files or query_database) and query:
        # Store the question and context for potential detailed report generation
        st.session_state.last_question = query
        st.session_state.last_context = {
            'query_database': query_database,
            'has_contract': contract_file is not None,
            'has_payout': payout_file is not None
        }
        
        # Determine analysis type
        if query_database:
            analysis_type = "🔍 Querying existing database"
        elif contract_file and payout_file:
            analysis_type = "📊 Analyzing contract vs payout discrepancies"
        elif contract_file:
            analysis_type = "📄 Analyzing contract document"
        else:
            analysis_type = "💰 Analyzing payout report"
        
        # Show progress with appropriate message
        with st.spinner(f"🔄 {analysis_type}..."):
            try:
                # Handle database-only queries
                if query_database and not has_files:
                    # For database queries, we'll call a simplified endpoint
                    try:
                        response = requests.post(
                            f"http://localhost:{settings.api_port}/query",
                            json={"question": query},
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            ai_response = result.get("answer", "No response received")
                            status = result.get("status", "success")
                            
                            # Handle different response types
                            if status == "no_documents":
                                st.warning("📂 Database is Empty")
                                st.info(ai_response)
                                suggestion = result.get("suggestion", "")
                                if suggestion:
                                    st.info(f"💡 **Suggestion:** {suggestion}")
                                    
                            elif status == "no_index":
                                st.warning("🔧 Database Not Initialized")
                                st.info(ai_response)
                                suggestion = result.get("suggestion", "")
                                if suggestion:
                                    st.info(f"💡 **Suggestion:** {suggestion}")
                                    
                            else:
                                # Display successful analysis
                                st.success("✅ Database Query Complete!")
                                
                                # Show document count if available
                                doc_count = result.get("documents_found")
                                if doc_count:
                                    st.info(f"📊 Searched across {doc_count} document chunks")
                                
                                # Display the AI response
                                st.markdown("### 🤖 AI Analysis")
                                st.markdown("**Your Question:**")
                                st.info(query)
                                st.markdown("**AI Response:**")
                                
                                # Escape LaTeX characters to prevent math rendering
                                def escape_latex(text):
                                    """Escape LaTeX special characters to prevent unwanted math rendering."""
                                    text = text.replace('$', '\\$')
                                    text = text.replace('_', '\\_')
                                    text = text.replace('^', '\\^')
                                    text = text.replace('#', '\\#')
                                    return text
                                
                                escaped_response = escape_latex(ai_response)
                                st.markdown(escaped_response)
                            
                        else:
                            st.error(f"❌ Query failed ({response.status_code})")
                            st.error("Database query endpoint may not be available. Please upload files instead.")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to the API server for database queries.")
                        st.info("💡 Try uploading files instead for local analysis.")
                    
                else:
                    # Prepare files for upload - handle single file case
                    files = {}
                    data = {
                        'question': query,
                        'query_database': str(query_database).lower(),  # Send the database query flag
                        'detailed_report': 'false'  # Default to concise analysis
                    }
                    
                    if contract_file:
                        files['contract_file'] = (contract_file.name, contract_file.getvalue(), contract_file.type)
                    else:
                        # Create a dummy contract file for single payout analysis
                        files['contract_file'] = ('dummy_contract.txt', b'No contract provided for this analysis.', 'text/plain')
                    
                    if payout_file:
                        files['payout_file'] = (payout_file.name, payout_file.getvalue(), payout_file.type)
                    else:
                        # Create a dummy payout file for single contract analysis
                        files['payout_file'] = ('dummy_payout.txt', b'No payout report provided for this analysis.', 'text/plain')
                    
                    # Call the /analyze endpoint
                    response = requests.post(
                        f"http://localhost:{settings.api_port}/analyze",
                        files=files,
                        data=data,
                        timeout=60  # 60 second timeout for analysis
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get("status") == "success" and result.get("analysis_successful"):
                            # Display successful analysis
                            st.success("✅ Analysis Complete!")
                            
                            # Display analysis details
                            with st.expander("📊 Analysis Details", expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Contract Processed", "✅" if result.get("contract_indexed") else "❌")
                                    st.text(f"File: {result.get('contract_file', 'N/A')}")
                                with col2:
                                    st.metric("Payout Report Processed", "✅" if result.get("payout_indexed") else "❌")
                                    st.text(f"File: {result.get('payout_file', 'N/A')}")
                            
                            # Display the AI's answer
                            st.markdown("## 🤖 AI Financial Analysis")
                            st.markdown("**Your Question:**")
                            st.info(result.get("question", query))
                            
                            st.markdown("**AI Response:**")
                            # Display the answer in a nice format
                            answer = result.get("answer", "No answer provided")
                            
                            # Escape LaTeX characters to prevent Streamlit from interpreting $ as math delimiters
                            def escape_latex(text):
                                """Escape LaTeX special characters to prevent unwanted math rendering."""
                                # Escape dollar signs and other LaTeX special characters
                                text = text.replace('$', '\\$')
                                text = text.replace('_', '\\_')
                                text = text.replace('^', '\\^')
                                text = text.replace('#', '\\#')
                                return text
                            
                            # Escape LaTeX and display the answer
                            escaped_answer = escape_latex(answer)
                            st.markdown(escaped_answer)
                            
                            # Show session info
                            st.markdown("---")
                            st.caption(f"Session ID: {result.get('session_id', 'N/A')}")
                            
                        else:
                            # Handle analysis errors
                            st.error("❌ Analysis Failed")
                            error_msg = result.get("error", "Unknown error occurred")
                            st.error(f"Error: {error_msg}")
                            
                            # Show what was processed
                            if result.get("contract_indexed"):
                                st.info("✅ Contract was processed successfully")
                            else:
                                st.warning("❌ Contract processing failed")
                                
                            if result.get("payout_indexed"):
                                st.info("✅ Payout report was processed successfully")
                            else:
                                st.warning("❌ Payout report processing failed")
                    
                    else:
                        # Handle HTTP errors
                        st.error(f"❌ Server Error ({response.status_code})")
                        try:
                            error_detail = response.json().get("detail", "Unknown server error")
                            st.error(f"Details: {error_detail}")
                        except:
                            st.error("Failed to get error details from server")
                        
            except requests.exceptions.Timeout:
                st.error("⏱️ Analysis timed out. Please try again with smaller files or a simpler question.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to the API server. Please ensure it's running on port 8000.")
            except Exception as e:
                st.error(f"💥 Unexpected error: {str(e)}")
    else:
        # Show appropriate warning based on what's missing
        if not query:
            st.warning("⚠️ Please enter a question to analyze the documents.")
        elif not has_files and not query_database:
            st.warning("⚠️ Please upload at least one document or check 'Query existing database'.")
        else:
            st.warning("⚠️ Please provide either document uploads or enable database querying, and enter a question.")

# Add some space
st.markdown("---")

# Key Features Section - Business Value Focus
st.markdown("### ✨ Key Features")
with st.expander("Platform Capabilities", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🤖 AI Contract Analysis**")
        st.caption("GPT-4 powered intelligent document analysis")
    with col2:
        st.markdown("**🔍 Discrepancy Detection**") 
        st.caption("Automatic identification of contract vs payout differences")
    with col3:
        st.markdown("**📊 Multi-Document Search**")
        st.caption("Semantic search across all partnership agreements")
    
    st.markdown("---")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("**⚡ Real-time Processing**")
        st.caption("Instant analysis of PDF and text documents")
    with col5:
        st.markdown("**🎨 Interactive Interface**")
        st.caption("User-friendly web application")
    with col6:
        st.markdown("**🏢 Enterprise Ready**")
        st.caption("Scalable architecture with OpenSearch backend")
    
    st.success("💼 Production-ready contract intelligence platform")
