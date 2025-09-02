# Contract Intelligence Assistant

## Overview

An AI-powered contract analysis system using RAG (Retrieval-Augmented Generation) technology. Built for food delivery platforms to automate legal document review, risk assessment, and contract insights generation across restaurant partnerships and vendor agreements.

## 🎯 Business Problem

Food delivery platforms manage hundreds of restaurant partnerships with complex contracts containing varying commission rates, exclusivity clauses, and performance metrics. Manual review is time-consuming and error-prone.

## 💡 Solution

Smart document analysis system that:
- **Automates contract review** - Extract key terms, identify risks, highlight important clauses
- **Provides intelligent insights** - Answer business questions about partner portfolio
- **Visualizes trends** - Performance analytics and risk distribution dashboards
- **Enables semantic search** - Find similar partners or contract terms instantly

## 🏗️ Technical Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI Core   │    │   OpenSearch    │
│                 │◄──►│                  │◄──►│   Vector DB     │
│ • File Upload   │    │ • RAG Pipeline   │    │ • Embeddings    │
│ • Chat Interface│    │ • LangChain      │    │ • Similarity    │
│ • Analytics     │    │ • OpenAI API     │    │   Search        │
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

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend API** | FastAPI | RESTful API, async processing |
| **AI Framework** | LangChain | RAG pipeline, document processing |
| **Vector Database** | OpenSearch | Semantic search, embeddings storage |
| **LLM Provider** | OpenAI GPT-4 | Text generation, question answering |
| **Frontend** | Streamlit | Interactive UI, data visualization |
| **Visualization** | Matplotlib | Charts and analytics dashboards |
| **Containerization** | Docker | Easy deployment and environment isolation |

## 📋 Features

### Core Features
- **Document Upload**: Support for PDF contracts and partnership agreements
- **Intelligent Q&A**: Natural language queries about partners and contracts
- **Risk Assessment**: Automated scoring based on contract terms
- **Partner Analytics**: Performance trends and comparative analysis
- **Semantic Search**: Find similar partners or contract clauses

### Sample Queries
- "What restaurants have commission rates above 25%?"
- "Which contracts expire in the next 6 months?"
- "Show me partners with exclusive delivery agreements"
- "Find restaurants similar to Pizza Palace in terms of performance"

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key
- 4GB RAM minimum

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/contract-intelligence-assistant
cd contract-intelligence-assistant

# Set environment variables
echo "OPENAI_API_KEY=your_key_here" > .env

# Start services
docker-compose up -d

# Access application
open http://localhost:8501  # Streamlit UI
open http://localhost:8000/docs  # FastAPI docs
```

### Project Structure
```
contract-intelligence-assistant/
├── src/
│   ├── api/                 # FastAPI backend
│   │   ├── main.py         # API endpoints
│   │   ├── models.py       # Pydantic models
│   │   └── services/       # Business logic
│   ├── rag/                # RAG pipeline
│   │   ├── document_processor.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   └── ui/                 # Streamlit interface
│       ├── app.py          # Main UI
│       ├── pages/          # Multi-page app
│       └── components/     # Reusable UI components
├── data/                   # Sample documents
├── docker-compose.yml      # Service orchestration  
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🔧 API Endpoints

### Document Management
```http
POST /api/documents/upload
Content-Type: multipart/form-data

Upload restaurant contracts for processing
```

### Intelligent Query
```http
POST /api/query
Content-Type: application/json

{
  "question": "What are the top risk factors in our contracts?",
  "filters": {"partner_type": "restaurant"}
}
```

### Analytics
```http
GET /api/analytics/dashboard

Returns partner performance metrics and trends
```

## 📊 Sample Data

The system comes with sample restaurant partnership contracts including:
- Commission agreements (15-30% ranges)
- Delivery zone definitions  
- Exclusivity clauses
- Performance SLAs
- Marketing cooperation terms

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Test API endpoints
pytest tests/api/

# Integration tests
pytest tests/integration/
```

## 📈 Performance Metrics

- **Document Processing**: ~30 seconds for 50-page contract
- **Query Response Time**: <3 seconds for complex questions
- **Similarity Search**: <1 second for 1000+ documents
- **Memory Usage**: ~2GB for 500 restaurant contracts

## 🔐 Security Considerations

- API key encryption in environment variables
- Input validation for document uploads
- Rate limiting on API endpoints
- Secure document storage with access logs

## 🚀 Deployment Options

### Local Development
```bash
docker-compose up -d
```

### Cloud Deployment (AWS)
- ECS with Fargate for scalability
- OpenSearch Service for managed vector store
- S3 for document storage
- CloudWatch for monitoring

## 🛣️ Roadmap

### Phase 1 (Current MVP)
- ✅ Basic RAG pipeline
- ✅ Document upload and processing
- ✅ Q&A interface
- ✅ Simple analytics

### Phase 2 (Future Enhancements)
- [ ] Multi-language support
- [ ] Advanced risk modeling
- [ ] Integration with legal databases
- [ ] Real-time contract monitoring
- [ ] Automated compliance checking

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions about implementation or deployment:
- Create an issue in GitHub repository
- Check documentation in `/docs` folder
- Review API documentation at `/docs` endpoint

---

*AI-powered solution for modern foodtech businesses*