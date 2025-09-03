"""
Application configuration using Pydantic Settings.
"""
from pydantic import Field
from pydantic_settings import BaseSettings
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
