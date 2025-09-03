# =============================================================================
# CONTRACT INTELLIGENCE ASSISTANT - PowerShell Setup
# Run from contract_intelligence_assistant folder
# =============================================================================

Write-Host "🚀 Setting up project structure..." -ForegroundColor Green

# =============================================================================
# CREATE FOLDER STRUCTURE
# =============================================================================

Write-Host "📁 Creating directories..." -ForegroundColor Yellow

# Main source structure
New-Item -ItemType Directory -Path "src" -Force | Out-Null
New-Item -ItemType Directory -Path "src\api" -Force | Out-Null
New-Item -ItemType Directory -Path "src\api\routers" -Force | Out-Null
New-Item -ItemType Directory -Path "src\services" -Force | Out-Null
New-Item -ItemType Directory -Path "src\infrastructure" -Force | Out-Null
New-Item -ItemType Directory -Path "src\infrastructure\opensearch" -Force | Out-Null
New-Item -ItemType Directory -Path "src\infrastructure\openai" -Force | Out-Null
New-Item -ItemType Directory -Path "src\models" -Force | Out-Null
New-Item -ItemType Directory -Path "src\core" -Force | Out-Null
New-Item -ItemType Directory -Path "src\ui" -Force | Out-Null

# Data directories
New-Item -ItemType Directory -Path "data" -Force | Out-Null
New-Item -ItemType Directory -Path "data\sample_contracts" -Force | Out-Null
New-Item -ItemType Directory -Path "data\uploads" -Force | Out-Null

# Test directories
New-Item -ItemType Directory -Path "tests" -Force | Out-Null
New-Item -ItemType Directory -Path "tests\unit" -Force | Out-Null
New-Item -ItemType Directory -Path "tests\integration" -Force | Out-Null

# Other directories
New-Item -ItemType Directory -Path "docs" -Force | Out-Null
New-Item -ItemType Directory -Path "scripts" -Force | Out-Null
New-Item -ItemType Directory -Path "logs" -Force | Out-Null

Write-Host "✅ Directories created!" -ForegroundColor Green

# =============================================================================
# CREATE PYTHON PACKAGE FILES (__init__.py)
# =============================================================================

Write-Host "📦 Creating Python packages..." -ForegroundColor Yellow

# Create __init__.py files for Python packages
New-Item -ItemType File -Path "src\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\api\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\api\routers\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\services\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\infrastructure\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\infrastructure\opensearch\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\infrastructure\openai\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\models\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\core\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "src\ui\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "tests\__init__.py" -Force | Out-Null

Write-Host "✅ Python packages created!" -ForegroundColor Green

# =============================================================================
# CREATE .ENV.TEMPLATE
# =============================================================================

Write-Host "⚙️ Creating .env.template..." -ForegroundColor Yellow

@"
# =============================================================================
# CONTRACT INTELLIGENCE ASSISTANT - Environment Configuration
# =============================================================================

# Application Settings
APP_NAME="Contract Intelligence Assistant"
APP_VERSION="1.0.0"
DEBUG=true
ENVIRONMENT=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI Configuration (REQUIRED - Add your key here!)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.1

# OpenSearch Configuration
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_INDEX_NAME=financial_documents

# Document Processing
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501

# Demo Configuration
DEMO_PARTNER_NAME="Sushi Express 24/7"
DEMO_PARTNER_ID="rest-789"
"@ | Out-File -FilePath ".env.template" -Encoding UTF8

Write-Host "✅ .env.template created!" -ForegroundColor Green

# =============================================================================
# CREATE CORE APPLICATION FILES
# =============================================================================

Write-Host "🔧 Creating core application files..." -ForegroundColor Yellow

# src/core/config.py
@"
"""
Application configuration using Pydantic Settings.
"""
from pydantic import BaseSettings, Field
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = Field(default="Contract Intelligence Assistant", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")
    
    # OpenSearch
    opensearch_host: str = Field(default="localhost", env="OPENSEARCH_HOST")
    opensearch_port: int = Field(default=9200, env="OPENSEARCH_PORT")
    opensearch_index_name: str = Field(default="financial_documents", env="OPENSEARCH_INDEX_NAME")
    
    # Document Processing
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Streamlit
    streamlit_server_port: int = Field(default=8501, env="STREAMLIT_SERVER_PORT")
    
    # Demo
    demo_partner_name: str = Field(default="Sushi Express 24/7", env="DEMO_PARTNER_NAME")
    demo_partner_id: str = Field(default="rest-789", env="DEMO_PARTNER_ID")
    
    @property
    def opensearch_url(self) -> str:
        """Construct OpenSearch URL."""
        return f"http://{self.opensearch_host}:{self.opensearch_port}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
"@ | Out-File -FilePath "src\core\config.py" -Encoding UTF8

# src/api/main.py
@"
"""
FastAPI main application for Contract Intelligence Assistant.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.core.config import settings

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

# TODO: Add /analyze endpoint here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
"@ | Out-File -FilePath "src\api\main.py" -Encoding UTF8

# src/ui/app.py
@"
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
    st.sidebar.info("Start API: `python src/api/main.py`")

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
"@ | Out-File -FilePath "src\ui\app.py" -Encoding UTF8

Write-Host "✅ Core application files created!" -ForegroundColor Green

# =============================================================================
# CREATE SAMPLE DATA
# =============================================================================

Write-Host "📄 Creating sample data..." -ForegroundColor Yellow

# Sample contract
@"
RESTAURANT PARTNERSHIP AGREEMENT
=================================

Restaurant Name: Sushi Express 24/7
Partner ID: rest-789
Contract Date: January 1, 2024

COMMISSION STRUCTURE:
• Base Commission Rate: 25.0% of gross order value
• Promotional Campaign Rate: 22.0% (during active campaigns)
• Volume Incentive: 23.0% if weekly GMV exceeds £4,000

FEES AND CHARGES:
• Delivery Service Fee: £2.00 per delivered order
• Marketing Contribution: 2.5% of monthly GMV
• Late Order Penalty: £8.00 per incident (>25 minutes prep)
• Service Processing Fee: £0.75 per order processed

PAYMENT TERMS:
• Weekly payments every Wednesday
• Currency: GBP (British Pounds)
• Net-7 payment terms

PROMOTIONAL CAMPAIGNS:
• January 2024: New Year Special (22% commission rate)
• Campaign codes: NY2024, NEWYEAR
"@ | Out-File -FilePath "data\sample_contracts\Sushi_Express_Contract.txt" -Encoding UTF8

# Sample payout report
@"
WEEKLY PAYOUT STATEMENT
=======================
Restaurant: Sushi Express 24/7
Partner ID: rest-789
Statement Period: January 15-21, 2024

ORDER SUMMARY:
Total Orders: 178
Orders Delivered: 172
Gross Order Value: £4,267.50
Average Order Value: £23.94

COMMISSION BREAKDOWN:
Regular Orders (145): £3,450.00 × 25.0% = £862.50
Promotional Orders (27): £697.50 × 22.0% = £153.45
Volume Bonus Applied: 23.0% rate (GMV > £4,000)
TOTAL COMMISSION: £981.53

ADDITIONAL EARNINGS:
Delivery Fees: 172 × £2.00 = £344.00

DEDUCTIONS:
Marketing Fee: £4,267.50 × 2.5% = -£106.69
Late Penalties: 3 incidents × £8.00 = -£24.00
Service Fees: 178 × £0.75 = -£133.50
TOTAL DEDUCTIONS: -£264.19

FINAL PAYOUT: £1,061.34

DISCREPANCY NOTES:
Expected commission (25%): £1,066.88
Actual commission: £981.53
Difference due to promotional rates and volume bonus applied
"@ | Out-File -FilePath "data\sample_contracts\Sushi_Express_Payout_Report.txt" -Encoding UTF8

Write-Host "✅ Sample data created!" -ForegroundColor Green

# =============================================================================
# CREATE DOCKER COMPOSE
# =============================================================================

Write-Host "🐳 Creating docker-compose.yml..." -ForegroundColor Yellow

@"
version: '3.8'

services:
  opensearch:
    image: opensearchproject/opensearch:2.11.1
    container_name: opensearch
    environment:
      - cluster.name=contract-intelligence
      - node.name=opensearch-node1
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
      - "DISABLE_INSTALL_DEMO_CONFIG=true"
      - "DISABLE_SECURITY_PLUGIN=true"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - opensearch-data:/usr/share/opensearch/data
    ports:
      - "9200:9200"
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  opensearch-dashboards:
    image: opensearchproject/opensearch-dashboards:2.11.1
    container_name: opensearch-dashboards
    ports:
      - "5601:5601"
    environment:
      OPENSEARCH_HOSTS: '["http://opensearch:9200"]'
      DISABLE_SECURITY_DASHBOARDS_PLUGIN: "true"
    depends_on:
      opensearch:
        condition: service_healthy
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  opensearch-data:
    driver: local
"@ | Out-File -FilePath "docker-compose.yml" -Encoding UTF8

Write-Host "✅ docker-compose.yml created!" -ForegroundColor Green

# =============================================================================
# CREATE BASIC TESTS
# =============================================================================

Write-Host "🧪 Creating basic test..." -ForegroundColor Yellow

@"
"""
Test configuration.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_config_import():
    """Test that config can be imported."""
    from src.core.config import settings
    assert settings.app_name == "Contract Intelligence Assistant"

def test_api_import():
    """Test that FastAPI app can be imported.""" 
    from src.api.main import app
    assert app.title == "Contract Intelligence Assistant"
"@ | Out-File -FilePath "tests\test_basic.py" -Encoding UTF8

Write-Host "✅ Basic test created!" -ForegroundColor Green

# =============================================================================
# SHOW PROJECT STRUCTURE
# =============================================================================

Write-Host "`n🎉 PROJECT SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

Write-Host "`n📁 Project structure created:" -ForegroundColor Cyan
tree /F | Select-Object -First 30

Write-Host "`n🚀 Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy .env.template to .env: " -NoNewline; Write-Host "copy .env.template .env" -ForegroundColor White
Write-Host "2. Add your OpenAI API key to .env file" -ForegroundColor White
Write-Host "3. Install dependencies: " -NoNewline; Write-Host "pip install -r requirements.txt" -ForegroundColor White  
Write-Host "4. Start OpenSearch: " -NoNewline; Write-Host "docker-compose up opensearch -d" -ForegroundColor White
Write-Host "5. Test FastAPI: " -NoNewline; Write-Host "python src/api/main.py" -ForegroundColor White
Write-Host "6. Test Streamlit: " -NoNewline; Write-Host "streamlit run src/ui/app.py" -ForegroundColor White

Write-Host "`n✅ Ready to implement TASK-1!" -ForegroundColor Green