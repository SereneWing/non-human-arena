"""Application configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Environment(Enum):
    """Application environment."""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Log level."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseModel):
    """Database configuration."""
    
    url: str = Field(default="sqlite+aiosqlite:///./data.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)


class RedisConfig(BaseModel):
    """Redis configuration."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)
    password: Optional[str] = Field(default=None)
    max_connections: int = Field(default=50)


class LLMConfig(BaseModel):
    """LLM configuration."""
    
    provider: str = Field(default="openai")
    api_key: str = Field(default="")
    base_url: Optional[str] = Field(default=None)
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    timeout: float = Field(default=60.0)
    max_retries: int = Field(default=3)


class LogConfig(BaseModel):
    """Log configuration."""
    
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_enabled: bool = Field(default=True)
    file_path: str = Field(default="logs/app.log")
    file_max_bytes: int = Field(default=10 * 1024 * 1024)
    file_backup_count: int = Field(default=5)
    console_enabled: bool = Field(default=True)


class AppConfig(BaseModel):
    """Application configuration."""
    
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    
    # Component configs
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    
    # Feature flags
    enable_heartbeat: bool = Field(default=True)
    enable_history: bool = Field(default=True)
    enable_webhook: bool = Field(default=False)
    
    # Session config
    session_timeout: int = Field(default=3600)
    max_sessions: int = Field(default=100)
    
    # CORS
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    
    # API
    api_prefix: str = Field(default="/api/v1")
    
    class Config:
        arbitrary_types_allowed = True


def load_config_from_env() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig(
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "true").lower() == "true",
        secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
        database=DatabaseConfig(
            url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data.db"),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
        ),
        redis=RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
        ),
        llm=LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
        ),
        log=LogConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_enabled=os.getenv("LOG_FILE_ENABLED", "true").lower() == "true",
            console_enabled=os.getenv("LOG_CONSOLE_ENABLED", "true").lower() == "true",
        ),
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        api_prefix=os.getenv("API_PREFIX", "/api/v1"),
    )


_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config_from_env()
    return _config


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset the global configuration."""
    global _config
    _config = None
