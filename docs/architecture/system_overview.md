# System Overview

This document provides a high-level overview of the Contract Intelligence Assistant system architecture and data flow.

## System Architecture Overview

```mermaid
graph TB
    subgraph "User Interface"
        UI[Streamlit Web App]
        API_CLIENT[API Client]
    end
    
    subgraph "API Layer"
        FASTAPI[FastAPI Router]
        AUTH[Authentication]
        MIDDLEWARE[Middleware]
    end
    
    subgraph "Business Logic"
        DOC_SVC[Document Processing Service]
        RAG_SVC[RAG Query Service]
        EMBED_SVC[Embedding Service]
        INDEX_SVC[Document Indexing Service]
    end
    
    subgraph "Data Processing"
        PDF_PROC[PDF Text Extraction]
        CHUNK[Text Chunking]
        EMBED_GEN[Embedding Generation]
        PROMPT_MGR[Prompt Management]
    end
    
    subgraph "External Services"
        OPENAI_API[OpenAI GPT-4 API]
        EMBED_API[OpenAI Embeddings API]
    end
    
    subgraph "Data Storage"
        OPENSEARCH[OpenSearch Vector DB]
        FILE_STORE[Document File Storage]
    end
    
    UI --> FASTAPI
    API_CLIENT --> FASTAPI
    FASTAPI --> AUTH
    FASTAPI --> MIDDLEWARE
    FASTAPI --> DOC_SVC
    FASTAPI --> RAG_SVC
    
    DOC_SVC --> PDF_PROC
    DOC_SVC --> INDEX_SVC
    INDEX_SVC --> CHUNK
    INDEX_SVC --> EMBED_SVC
    
    RAG_SVC --> PROMPT_MGR
    RAG_SVC --> OPENSEARCH
    RAG_SVC --> OPENAI_API
    
    EMBED_SVC --> EMBED_GEN
    EMBED_GEN --> EMBED_API
    EMBED_SVC --> OPENSEARCH
    
    PDF_PROC --> FILE_STORE
    CHUNK --> OPENSEARCH
    
    style UI fill:#e3f2fd
    style FASTAPI fill:#e8f5e8
    style OPENSEARCH fill:#fff3e0
    style OPENAI_API fill:#f3e5f5
    style FILE_STORE fill:#fce4ec
```

## System Components

### User Interface Layer
- **Streamlit Web App**: Primary user interface for contract analysis
- **API Client**: Direct API access for programmatic integration

### API Layer
- **FastAPI Router**: RESTful API endpoints for all system functionality
- **Authentication**: User authentication and authorization
- **Middleware**: Request/response processing and logging

### Business Logic Layer
- **Document Processing Service**: Handles contract upload and processing
- **RAG Query Service**: Manages intelligent query processing and response generation
- **Embedding Service**: Creates and manages document embeddings
- **Document Indexing Service**: Handles document indexing and search preparation

### Data Processing Pipeline
- **PDF Text Extraction**: Converts PDF contracts to text using advanced parsing
- **Text Chunking**: Splits documents into semantically meaningful chunks
- **Embedding Generation**: Creates vector representations of text chunks
- **Prompt Management**: Manages different prompt templates for various query types

### External Dependencies
- **OpenAI GPT-4 API**: Advanced natural language processing and analysis
- **OpenAI Embeddings API**: Text embedding generation for semantic search

### Data Storage
- **OpenSearch Vector Database**: Stores document embeddings and enables semantic search
- **Document File Storage**: Persistent storage for original contract files

## Key Data Flows

### Document Upload Flow
1. User uploads contract via Streamlit UI
2. FastAPI receives and validates document
3. Document Processing Service extracts text from PDF
4. Text is chunked into manageable segments
5. Embedding Service generates vector embeddings
6. Document Indexing Service stores embeddings in OpenSearch

### Query Processing Flow
1. User submits query via UI or API
2. RAG Service determines query type (simple vs complex)
3. Appropriate prompt template is selected
4. Semantic search retrieves relevant document chunks
5. Context is assembled with relevant documents
6. OpenAI GPT-4 processes query with context
7. Response is returned to user

## Performance Characteristics

- **Document Processing**: 5-10 seconds per contract for full indexing
- **Query Response**: Sub-second for simple queries, 2-5 seconds for complex analysis
- **Concurrent Users**: Supports multiple simultaneous users
- **Document Capacity**: Scalable to thousands of contracts

## Integration Points

- **REST API**: Full programmatic access to all functionality
- **Webhook Support**: Can be extended for real-time notifications
- **Batch Processing**: Supports bulk document processing
- **Export Capabilities**: Analysis results can be exported in various formats
