# 🚀 Docker Deployment Guide

## Quick Start (One Command Deployment)

```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY=your_actual_api_key_here

# 2. Start all services
docker-compose up -d

# 3. Access the application
# - Streamlit UI: http://localhost:8501
# - FastAPI: http://localhost:8000
# - OpenSearch: http://localhost:9200
# - OpenSearch Dashboard: http://localhost:5601
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                 Docker Network                  │
├─────────────────────────────────────────────────┤
│  📱 Streamlit UI (8501)                        │
│  🔗 FastAPI Backend (8000)                     │
│  🔍 OpenSearch Engine (9200)                   │
│  📊 OpenSearch Dashboard (5601)                │
└─────────────────────────────────────────────────┘
```

## 🛠️ Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### Step-by-Step Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd contract_intelligence_assistant
   ```

2. **Set environment variables**
   ```bash
   # Option 1: Export environment variable
   export OPENAI_API_KEY=your_actual_api_key_here
   
   # Option 2: Create .env file
   cp .env.docker .env
   # Edit .env file with your OpenAI API key
   ```

3. **Deploy with Docker Compose**
   ```bash
   # Build and start all services
   docker-compose up -d
   
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

4. **Access the application**
   - **Main UI**: http://localhost:8501 (Streamlit)
   - **API Docs**: http://localhost:8000/docs (FastAPI)
   - **Health Check**: http://localhost:8000/health
   - **OpenSearch**: http://localhost:9200
   - **OpenSearch Dashboard**: http://localhost:5601

## 🔧 Development Mode

```bash
# Run with live reload for development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Attach to application logs
docker-compose logs -f contract-intelligence-app
```

## 📊 Service Health Checks

```bash
# Check all services health
docker-compose ps

# Test API health
curl http://localhost:8000/health

# Test OpenSearch health  
curl http://localhost:9200/_cluster/health
```

## 🛑 Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears data)
docker-compose down -v
```

## 🚢 Production Deployment

For production deployment on any machine:

1. **Transfer files**
   ```bash
   # Copy these files to target machine:
   - docker-compose.yml
   - Dockerfile
   - requirements.txt
   - src/ folder
   - data/ folder (optional sample data)
   ```

2. **Set production environment**
   ```bash
   export OPENAI_API_KEY=your_production_key
   export ENVIRONMENT=production
   export DEBUG=false
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

## 💡 Benefits of This Approach

✅ **Single Command Deployment** - `docker-compose up -d`
✅ **Environment Consistency** - Same setup everywhere
✅ **Easy Sharing** - Send to team/interviewers easily
✅ **Production Ready** - Professional deployment approach
✅ **Network Isolation** - All services communicate internally
✅ **Health Monitoring** - Built-in health checks
✅ **Data Persistence** - OpenSearch data persisted in volumes
✅ **Scalable** - Easy to add more services

## 🔍 Troubleshooting

```bash
# View service logs
docker-compose logs contract-intelligence-app
docker-compose logs opensearch
docker-compose logs opensearch-dashboards

# Restart specific service
docker-compose restart contract-intelligence-app

# Rebuild application image
docker-compose build contract-intelligence-app
docker-compose up -d contract-intelligence-app
```

## 📝 Notes for Interviewers

This Docker setup demonstrates:
- **Professional deployment practices**
- **Microservices architecture**
- **Container orchestration**
- **Environment management**
- **Production readiness**

Start with: `docker-compose up -d` and access http://localhost:8501
