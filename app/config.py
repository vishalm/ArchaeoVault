"""
Configuration management for ArchaeoVault following 12-Factor App principles.

This module handles all configuration through environment variables,
providing type-safe configuration with validation and defaults.
"""

import os
from functools import lru_cache
from typing import List, Optional, Union
from pydantic import Field, validator, ConfigDict
from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import BaseSettings



class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(
        default="postgresql://archaeo:archaeo123@localhost:5432/archaeovault",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    host: str = Field(default="localhost", env="DATABASE_HOST")
    port: int = Field(default=5432, env="DATABASE_PORT")
    name: str = Field(default="archaeovault", env="DATABASE_NAME")
    user: str = Field(default="archaeo", env="DATABASE_USER")
    password: str = Field(default="archaeo123", env="DATABASE_PASSWORD")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    pool_overflow: int = Field(default=20, env="DATABASE_POOL_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    model_config = ConfigDict(env_prefix = "DATABASE_")
class RedisSettings(BaseSettings):
    """Redis cache configuration settings."""
    
    url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="Redis connection URL"
    )
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    pool_timeout: int = Field(default=30, env="REDIS_POOL_TIMEOUT")
    
    model_config = ConfigDict(env_prefix = "DATABASE_")
class AISettings(BaseSettings):
    """AI services configuration settings."""
    
    anthropic_api_key: str = Field(
        default="",
        env="ANTHROPIC_API_KEY",
        description="Anthropic Claude API key (required)"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        env="OPENAI_API_KEY",
        description="OpenAI API key (optional)"
    )
    default_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        env="DEFAULT_AI_MODEL",
        description="Default AI model to use"
    )
    temperature: float = Field(
        default=0.7,
        env="AI_MODEL_TEMPERATURE",
        ge=0.0,
        le=2.0,
        description="AI model temperature"
    )
    max_tokens: int = Field(
        default=4000,
        env="AI_MODEL_MAX_TOKENS",
        gt=0,
        description="Maximum tokens for AI responses"
    )
    timeout: int = Field(
        default=30,
        env="AI_MODEL_TIMEOUT",
        gt=0,
        description="AI model request timeout in seconds"
    )
    
    # Agent configuration
    agent_pool_size: int = Field(default=5, env="AI_AGENT_POOL_SIZE")
    agent_max_retries: int = Field(default=3, env="AI_AGENT_MAX_RETRIES")
    agent_retry_delay: int = Field(default=1, env="AI_AGENT_RETRY_DELAY")
    agent_cache_ttl: int = Field(default=3600, env="AI_AGENT_CACHE_TTL")
    
    model_config = ConfigDict(env_prefix = "DATABASE_")
class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        env="SECRET_KEY",
        description="Application secret key"
    )
    jwt_secret_key: str = Field(
        default="your-jwt-secret-key-here",
        env="JWT_SECRET_KEY",
        description="JWT secret key"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )
    
    # Password hashing
    password_hash_algorithm: str = Field(default="bcrypt", env="PASSWORD_HASH_ALGORITHM")
    password_hash_rounds: int = Field(default=12, env="PASSWORD_HASH_ROUNDS")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests_per_minute: int = Field(
        default=60,
        env="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )
    rate_limit_burst_size: int = Field(default=10, env="RATE_LIMIT_BURST_SIZE")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:8501", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_METHODS"
    )
    cors_headers: List[str] = Field(
        default=["Content-Type", "Authorization"],
        env="CORS_HEADERS"
    )
    
    @validator("cors_origins", "cors_methods", "cors_headers", pre=True)
    def parse_list_strings(cls, v):
        """Parse comma-separated strings into lists."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    model_config = ConfigDict(env_prefix = "DATABASE_")
class StorageSettings(BaseSettings):
    """File storage configuration settings."""
    
    storage_type: str = Field(default="local", env="STORAGE_TYPE")
    storage_path: str = Field(default="./uploads", env="STORAGE_PATH")
    max_upload_size_mb: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    allowed_file_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp", "application/pdf"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # AWS S3 configuration
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    @validator("allowed_file_types", pre=True)
    def parse_file_types(cls, v):
        """Parse comma-separated file types into list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v
    
    model_config = ConfigDict(env_prefix = "DATABASE_")
class StreamlitSettings(BaseSettings):
    """Streamlit configuration settings."""
    
    port: int = Field(default=8501, env="STREAMLIT_PORT")
    host: str = Field(default="0.0.0.0", env="STREAMLIT_HOST")
    headless: bool = Field(default=True, env="STREAMLIT_HEADLESS")
    server_run_on_save: bool = Field(default=True, env="STREAMLIT_SERVER_RUN_ON_SAVE")
    server_file_watcher_type: str = Field(default="auto", env="STREAMLIT_SERVER_FILE_WATCHER_TYPE")
    browser_gather_usage_stats: bool = Field(default=False, env="STREAMLIT_BROWSER_GATHER_USAGE_STATS")
    
    model_config = ConfigDict(env_prefix = "DATABASE_")
class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    file_path: str = Field(default="./logs/app.log", env="LOG_FILE_PATH")
    max_size_mb: int = Field(default=100, env="LOG_MAX_SIZE_MB")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # Structured logging
    structured: bool = Field(default=True, env="LOG_STRUCTURED")
    include_timestamp: bool = Field(default=True, env="LOG_INCLUDE_TIMESTAMP")
    include_level: bool = Field(default=True, env="LOG_INCLUDE_LEVEL")
    include_module: bool = Field(default=True, env="LOG_INCLUDE_MODULE")
    
    model_config = ConfigDict(env_prefix = "DATABASE_")
class FeatureFlags(BaseSettings):
    """Feature flags configuration."""
    
    # AI Features
    enable_ai_analysis: bool = Field(default=True, env="ENABLE_AI_ANALYSIS")
    enable_ai_agents: bool = Field(default=True, env="ENABLE_AI_AGENTS")
    enable_ai_orchestration: bool = Field(default=True, env="ENABLE_AI_ORCHESTRATION")
    enable_ai_memory: bool = Field(default=True, env="ENABLE_AI_MEMORY")
    
    # 3D Features
    enable_3d_viewer: bool = Field(default=True, env="ENABLE_3D_VIEWER")
    enable_3d_modeling: bool = Field(default=True, env="ENABLE_3D_MODELING")
    enable_vr_support: bool = Field(default=False, env="ENABLE_VR_SUPPORT")
    
    # Advanced Features
    enable_real_time_collaboration: bool = Field(default=False, env="ENABLE_REAL_TIME_COLLABORATION")
    enable_mobile_app: bool = Field(default=False, env="ENABLE_MOBILE_APP")
    enable_api_access: bool = Field(default=True, env="ENABLE_API_ACCESS")
    enable_webhooks: bool = Field(default=False, env="ENABLE_WEBHOOKS")
    
    model_config = ConfigDict(env_prefix = "DATABASE_")
class Settings(PydanticBaseSettings):
    """Main application settings combining all configuration sections."""
    
    # Application metadata
    app_name: str = Field(default="ArchaeoVault", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_env: str = Field(default="development", env="APP_ENV")
    debug_mode: bool = Field(default=True, env="DEBUG_MODE")
    
    # Configuration sections
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    ai: AISettings = Field(default_factory=AISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    streamlit: StreamlitSettings = Field(default_factory=StreamlitSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    
    # External services
    mapbox_token: Optional[str] = Field(default=None, env="MAPBOX_TOKEN")
    museum_api_key: Optional[str] = Field(default=None, env="MUSEUM_API_KEY")
    museum_api_url: Optional[str] = Field(default=None, env="MUSEUM_API_URL")
    academic_api_key: Optional[str] = Field(default=None, env="ACADEMIC_API_KEY")
    academic_api_url: Optional[str] = Field(default=None, env="ACADEMIC_API_URL")
    
    model_config = ConfigDict(env_prefix = "DATABASE_", env_file = ".env", env_file_encoding = "utf-8", case_sensitive = False, validate_assignment = True)
    @validator("app_env")
    def validate_app_env(cls, v):
        """Validate application environment."""
        valid_envs = ["development", "staging", "production", "testing"]
        if v not in valid_envs:
            raise ValueError(f"app_env must be one of {valid_envs}")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.app_env == "testing"
    
    def get_database_url(self) -> str:
        """Get formatted database URL."""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get formatted Redis URL."""
        return self.redis.url
    
    def get_ai_client_config(self) -> dict:
        """Get AI client configuration."""
        return {
            "api_key": self.ai.anthropic_api_key,
            "model": self.ai.default_model,
            "temperature": self.ai.temperature,
            "max_tokens": self.ai.max_tokens,
            "timeout": self.ai.timeout,
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    This function uses lru_cache to ensure settings are loaded only once
    and cached for subsequent calls, following 12-Factor App principles.
    
    Returns:
        Settings: Application configuration object
    """
    return Settings()


# Global settings instance
settings = get_settings()
