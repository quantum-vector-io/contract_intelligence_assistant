# 🤖 Contract Intelligence Assistant

> AI-powered contract analysis system using RAG (Retrieval-Augmented Generation) for intelligent document processing and financial discrepancy detection.

## 🎯 Overview

A production-ready contract intelligence platform that combines **OpenAI GPT-4**, **OpenSearch vector database**, and **LangChain RAG pipeline** to provide automated analysis of partnership agreements and payout reports. Built for financial teams who need to quickly identify discrepancies and extract insights from large document volumes.

## ✨ Key Features

🔍 **Intelligent Document Analysis** - AI-powered contract and payout report processing  
📊 **Discrepancy Detection** - Automatic identification of contract vs payout differences  
🔎 **Semantic Search** - Query across all documents using natural language  
⚡ **Real-time Processing** - Instant analysis of PDF and text documents  
🌐 **Web Interface** - User-friendly Streamlit UI with API backend  
🐳 **Docker Ready** - One-command deployment with Docker Compose

## 🏗️ Architecture

### High-Level System Design
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI Core   │    │   OpenSearch    │
│                 │◄──►│                  │◄──►│   Vector DB     │
│ • File Upload   │    │ • RAG Pipeline   │    │ • Embeddings    │
│ • Chat Interface│    │ • LangChain      │    │ • Similarity    │
│ • Database Query│    │ • OpenAI API     │    │   Search        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Document       │
                       │   Processing     │
                       │ • PDF Parse      │
                       │ • Chunking       │
                       │ • Embedding      │
                       └──────────────────┘
```

### Docker Stack Deployment
```
┌─────────────────────────────────────────────────┐
│                 Docker Stack                   │
├─────────────────────────────────────────────────┤
│  📱 Streamlit UI (8501)                        │
│  🔗 FastAPI Backend (8000)                     │
│  🔍 OpenSearch Engine (9200)                   │
│  📊 OpenSearch Dashboard (5601)                │
└─────────────────────────────────────────────────┘
```

### RAG Pipeline Flow
```
Document Upload → PDF Processing → Text Chunking → OpenAI Embeddings → 
OpenSearch Storage → User Query → Semantic Search → Context Retrieval → 
GPT-4 Analysis → Response Generation
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI/ML** | OpenAI GPT-4 + LangChain | RAG pipeline, document analysis |
| **Vector DB** | OpenSearch | Semantic search, embeddings storage |
| **Backend** | FastAPI | RESTful API, async processing |
| **Frontend** | Streamlit | Interactive UI, file upload |
| **Deployment** | Docker Compose | Container orchestration |

## 🚀 Quick Start

### One-Command Deployment

**Option 1: Using .env file (Recommended)**
```bash
# 1. Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here

# 2. Start all services
docker-compose up -d

# 3. Access the application
open http://localhost:8501    # Main UI
open http://localhost:8000    # API docs
```

**Option 2: Environment variable**
```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY=your_actual_api_key_here

# 2. Start all services
docker-compose up -d
```

### Manual Setup (Development)

```bash
# Clone and setup
git clone <repository-url>
cd contract_intelligence_assistant

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start OpenSearch services only
docker-compose up -d opensearch opensearch-dashboards

# Start backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend (in another terminal)
streamlit run src/ui/app.py
```

## 💼 Usage Examples

### Upload & Analyze Documents
1. **Upload Files** - Contract and/or payout report
2. **Ask Questions** - Natural language queries
3. **Get AI Analysis** - Instant insights and discrepancy detection

### Sample Questions
```
• "What is the commission rate in this contract?"
• "Are there any discrepancies between contract terms and payouts?"
• "What promotional campaigns are mentioned?"
• "Show me all volume incentive terms"
• "Which contracts have the best profit margins?"
```

### Database Queries
Enable "Query existing database" to search across all previously uploaded documents without new uploads.

## 🧪 Testing

### Run Test Suite
```bash
# All tests
python run_tests.py

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Quick verification
curl http://localhost:8000/health
```

### Test Status
✅ **18/19 unit tests passing**  
✅ **Integration tests functional**  
✅ **API endpoints working**  
✅ **Docker deployment tested**

## 📁 Project Structure

```
contract_intelligence_assistant/
├── src/
│   ├── api/
│   │   ├── main.py                    # FastAPI application entry point
│   │   └── routers/
│   │       ├── documents.py           # Document upload endpoints
│   │       ├── financial_analysis.py  # Analysis endpoints
│   │       └── opensearch.py          # Search endpoints
│   ├── services/
│   │   ├── rag_service.py             # RAG pipeline with LangChain
│   │   ├── document_indexing_service.py # Document processing
│   │   ├── document_service.py        # File handling
│   │   ├── opensearch_service.py      # Vector database operations
│   │   ├── embedding_service.py       # OpenAI embeddings
│   │   └── langchain_document_service.py # LangChain integration
│   ├── infrastructure/
│   │   ├── opensearch/               # OpenSearch client setup
│   │   └── openai/                   # OpenAI client configuration
│   ├── models/                       # Pydantic data models
│   ├── core/
│   │   └── config.py                 # Configuration management
│   └── ui/
│       └── app.py                    # Streamlit interface
├── tests/
│   ├── unit/                         # Component tests
│   │   ├── test_basic.py             # Basic functionality
│   │   ├── test_openai.py            # OpenAI integration
│   │   └── test_opensearch_service.py # OpenSearch tests
│   ├── integration/                  # End-to-end tests
│   │   ├── test_complete_indexing.py # Full workflow tests
│   │   ├── test_financial_analysis_api.py # API testing
│   │   ├── test_system_integration.py # System integration
│   │   └── test_ui_workflow.py       # UI workflow tests
│   └── conftest.py                   # Test configuration & fixtures
├── data/
│   ├── sample_contracts/             # Demo contract documents
│   │   ├── *.pdf                     # Sample partnership agreements
│   │   └── *.txt                     # Processed contract data
│   └── uploads/                      # User uploaded files
├── docs/                            # Documentation
├── logs/                            # Application logs
├── scripts/
│   └── test_opensearch_api.py       # OpenSearch API testing
├── docker-compose.yml               # Service orchestration
├── Dockerfile                       # Multi-service container
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project configuration
├── setup.ps1                        # Windows setup script
├── setup-docker.ps1                 # Docker setup automation
├── DOCKER_DEPLOYMENT.md             # Docker deployment guide
└── run_tests.py                     # Test runner script
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional (with defaults)
OPENSEARCH_HOST=localhost      # Use 'opensearch' in Docker
OPENSEARCH_PORT=9200
OPENAI_MODEL=gpt-4o-mini
API_PORT=8000
```

### Docker Environment
The application automatically configures for Docker networking when deployed via Docker Compose.

## � Performance

- **Document Processing**: PDF chunks processed in ~10-30 seconds
- **Query Response**: AI analysis typically completes in 15-45 seconds  
- **Vector Search**: Sub-second semantic search across documents
- **Concurrent Users**: Supports multiple simultaneous analyses

## �️ Production Ready

✅ **Error Handling** - Comprehensive error handling and logging  
✅ **Health Checks** - Built-in health monitoring for all services  
✅ **Configuration** - Environment-based configuration management  
✅ **Testing** - Unit and integration test coverage  
✅ **Documentation** - API docs available at `/docs`  
✅ **Containerization** - Production Docker deployment

## � Deployment Options

### Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Manual Deployment
Individual service startup for development or custom deployments.

### Cloud Deployment
Ready for deployment on AWS ECS, Azure Container Instances, or any Docker-compatible platform.

## � Demo Data

The system includes sample contracts from food delivery partnerships:
- **Just Eat UK** - Partnership agreement with commission structures
- **Lieferando DE** - German partnership contract
- **Thuisbezorgd NL** - Netherlands enterprise addendum  
- **SkipTheDishes CA** - Canadian restaurant services agreement
- **Sushi Express** - Contract with payout reports for discrepancy analysis

## 📈 Key Metrics

**Documents Indexed**: 30+ contract chunks in OpenSearch  
**Response Accuracy**: High-quality GPT-4 powered analysis  
**Search Performance**: Vector similarity search across all documents  
**Deployment Time**: <5 minutes with Docker Compose

## 🤝 Contributing

This is a demonstration project showcasing production-ready AI application development with modern tools and best practices.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**🎯 Ready for production • 🐳 Docker enabled • 🤖 AI powered**