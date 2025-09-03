"""
Streamlit UI for Contract Intelligence Assistant.
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

if st.button("🔍 Analyze", type="primary"):
    # Check if we have files, database query option, and a question
    has_files = contract_file or payout_file
    
    if (has_files or query_database) and query:
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
                            
                            # Display successful analysis
                            st.success("✅ Database Query Complete!")
                            
                            # Display the AI response
                            st.markdown("### 🤖 AI Analysis")
                            st.markdown("**Your Question:**")
                            st.info(query)
                            st.markdown("**AI Response:**")
                            st.markdown(ai_response)
                            
                        else:
                            st.error(f"❌ Query failed ({response.status_code})")
                            st.error("Database query endpoint may not be available. Please upload files instead.")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to the API server for database queries.")
                        st.info("💡 Try uploading files instead for local analysis.")
                    
                else:
                    # Prepare files for upload - handle single file case
                    files = {}
                    data = {'question': query}
                    
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
                            st.markdown(answer)
                            
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
st.markdown("### � Key Features")
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
