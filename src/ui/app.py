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
query = st.text_area(
    "Your Question",
    placeholder="Example: Why is my commission different from the contract?",
    height=100
)

if st.button("🔍 Analyze", type="primary"):
    if contract_file and payout_file and query:
        st.success("Ready to analyze! (Feature coming in next steps)")
    else:
        st.warning("Please upload both documents and enter a question.")

# Footer
st.markdown("---")
st.markdown("📋 **Next Steps:** Implement document processing and AI analysis")
