"""
Application configuration management using Pydantic Settings.

This module defines the centralized configuration for the Contract Intelligence
Assistant platform. It uses Pydantic Settings to handle environment variables
and provide type-safe configuration management with default values and
validation.

The settings cover all major components including API servers, OpenAI integration,
OpenSearch configuration, document processing parameters, and demo data settings.
"""
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application configuration settings with environment variable support.
    
    Centralizes all application configuration including API settings, 
    external service credentials, processing parameters, and feature flags.
    Values can be overridden via environment variables following the
    standard naming convention.
    
    Attributes:
        app_name (str): Application display name.
        app_version (str): Current application version.
        debug (bool): Debug mode flag for development features.
        environment (str): Deployment environment identifier.
        api_host (str): API server bind address.
        api_port (int): API server port number.
        openai_api_key (str, optional): OpenAI API authentication key.
        openai_model (str): OpenAI model identifier for completions.
        openai_temperature (float): Model temperature for response variability.
        opensearch_host (str): OpenSearch server hostname.
        opensearch_port (int): OpenSearch server port number.
        opensearch_index_name (str): Default document index name.
        max_file_size_mb (int): Maximum allowed file upload size in MB.
        chunk_size (int): Document chunking size for processing.
        chunk_overlap (int): Overlap size between document chunks.
        streamlit_server_port (int): Streamlit frontend server port.
        demo_partner_name (str): Default partner name for demos.
        demo_partner_id (str): Default partner ID for demos.
    """
    
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
        """Construct the complete OpenSearch connection URL.
        
        Combines the configured host and port into a complete HTTP URL
        for OpenSearch client connections.
        
        Returns:
            str: Complete OpenSearch URL (e.g., "http://localhost:9200").
        """
        return f"http://{self.opensearch_host}:{self.opensearch_port}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
