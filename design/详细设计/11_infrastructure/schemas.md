# Infrastructure 模块数据结构

## 一、基础设施层架构

基础设施模块负责提供系统运行所需的基础服务，包括：
- 数据库连接管理
- 缓存管理
- 消息队列
- 配置管理
- 日志系统
- 监控和指标

## 二、配置管理

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum

class Environment(Enum):
    """运行环境"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    database: str = "non_human_arena"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 50

@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "openai"
    api_key: str = ""
    base_url: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: float = 60.0
    max_retries: int = 3

@dataclass
class AppConfig:
    """应用配置"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    secret_key: str = ""
    
    # 组件配置
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    
    # 功能开关
    enable_heartbeat: bool = True
    enable_history: bool = True
    enable_webhook: bool = False
    
    # 会话配置
    session_timeout: int = 3600
    max_sessions: int = 100
    
    # CORS配置
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
```

## 三、日志配置

```python
from dataclasses import dataclass
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogConfig:
    """日志配置"""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # 文件配置
    file_enabled: bool = True
    file_path: str = "logs/app.log"
    file_max_bytes: int = 10 * 1024 * 1024  # 10MB
    file_backup_count: int = 5
    
    # 控制台配置
    console_enabled: bool = True
    
    # 日志分级
    loggers: Dict[str, LogLevel] = field(default_factory=dict)
```

## 四、监控指标

```python
@dataclass
class MetricsConfig:
    """监控指标配置"""
    enabled: bool = True
    port: int = 9090
    
    # 指标收集
    collect_interval: int = 60  # 秒
    
    # 应用指标
    track_request_duration: bool = True
    track_database_queries: bool = True
    track_llm_calls: bool = True
    
    # 自定义指标
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthCheckConfig:
    """健康检查配置"""
    enabled: bool = True
    port: int = 8080
    path: str = "/health"
    
    # 检查项
    check_database: bool = True
    check_redis: bool = True
    check_llm: bool = True
```

## 五、异常处理

```python
@dataclass
class ErrorResponse:
    """错误响应"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

class ErrorCode:
    """错误码定义"""
    # 通用错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    
    # 会话错误
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_NOT_RUNNING = "SESSION_NOT_RUNNING"
    SESSION_TIMEOUT = "SESSION_TIMEOUT"
    
    # LLM错误
    LLM_API_ERROR = "LLM_API_ERROR"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_RATE_LIMIT = "LLM_RATE_LIMIT"
    
    # 规则错误
    RULE_VIOLATION = "RULE_VIOLATION"
    RULE_NOT_FOUND = "RULE_NOT_FOUND"
```
