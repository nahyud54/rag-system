"""Configuration settings for RAG System"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Server
    fast_api_host: str = "0.0.0.0"
    fast_api_port: int = 8000
    debug: bool = True

    # LLM Configuration
    llm_model: str = "qwen2.5"
    llm_api_key: str = ""
    llm_base_url: str = "http://localhost:11434"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048

    # Embedding Configuration
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_batch_size: int = 32
    embedding_device: str = "cpu"  # or 'cuda'

    # Vector Store Configuration
    vector_db_type: str = "chroma"
    vector_db_path: str = "./data/chroma_db"
    pinecone_api_key: str = ""
    pinecone_index_name: str = "rag-index"
    pinecone_environment: str = "gcp-starter"
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: str = ""

    # Retrieval Configuration
    top_k_results: int = 5
    similarity_threshold: float = 0.5
    use_multi_query: bool = True
    use_hyde: bool = False
    use_reranking: bool = True

    # Reranker Configuration
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_threshold: float = 0.5

    # Indexing Configuration
    chunk_size: int = 500
    chunk_overlap: int = 50
    min_chunk_size: int = 100

    # Raw data path
    raw_pptx_path: str = "../raw_pptx"

    # Crawling Configuration
    cookies_path: str = "./cookies.json"
    crawl_timeout: int = 30
    max_retries: int = 3

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text

    # Database
    database_url: str = "sqlite:///./data/rag.db"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
    ]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

    # Session
    session_timeout: int = 3600  # 1 hour
    max_sessions: int = 100

    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (cached)"""
    return Settings()


# Export settings instance
settings = get_settings()
