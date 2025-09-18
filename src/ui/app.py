"""
Clean Streamlit interface for Contract Intelligence Assistant with Dashboard.
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

# Navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select Page:",
    ["🔍 Document Analysis", "📊 Analytics Dashboard"],
    index=0,
    help="Choose between document analysis and dashboard views"
)

if page == "📊 Analytics Dashboard":
    # Revolutionary dashboard with holographic design
    try:
        # Clear any existing error state
        if 'dashboard_error' in st.session_state:
            del st.session_state.dashboard_error
        
        from src.ui.dashboard_revolutionary import render_revolutionary_dashboard
        render_revolutionary_dashboard()
        
    except ImportError as e:
        st.error(f"Dashboard module not available: {e}")
        st.info("Dashboard functionality requires additional dependencies.")
        st.code("pip install plotly==5.17.0")
        st.session_state.dashboard_error = f"ImportError: {e}"
        
    except Exception as e:
        st.error(f"Dashboard error: {e}")
        st.code(f"Error details: {str(e)}")
        
        # Show stack trace for debugging
        import traceback
        st.code(f"Stack trace:\n{traceback.format_exc()}")
        st.session_state.dashboard_error = f"Exception: {e}"
        
        # Show dashboard data check
        st.info("🔍 Debugging Information:")
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            st.success(f"✅ API Health: {response.status_code}")
        except Exception as api_e:
            st.error(f"❌ API Error: {api_e}")
        
        try:
            import plotly
            st.success(f"✅ Plotly version: {plotly.__version__}")
        except Exception as plotly_e:
            st.error(f"❌ Plotly Error: {plotly_e}")
            
        try:
            import pandas as pd
            st.success(f"✅ Pandas version: {pd.__version__}")
        except Exception as pandas_e:
            st.error(f"❌ Pandas Error: {pandas_e}")

else:
    # Document Analysis page  
    st.header("Document Analysis")
    
    # API Status check
    st.sidebar.markdown("---")
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

    # File upload section
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

    # Ask button
    col_ask1, col_ask2 = st.columns([2, 1])
    with col_ask1:
        ask_button_clicked = st.button("🔍 Ask", type="primary", help="Ask your question and get an analysis")
    with col_ask2:
        st.write("")  # Empty space

    if ask_button_clicked:
        if query and (contract_file or payout_file or query_database):
            st.success("🔄 Processing your question...")
            st.info("This is a simplified version. Full analysis functionality is available in the complete app.")
        else:
            st.warning("⚠️ Please provide a question and either upload files or enable database querying.")

    # Additional info
    st.markdown("---")
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
        
        st.success("💼 Production-ready contract intelligence platform")