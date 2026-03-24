# Infrastructure 模块服务层

## 一、数据库服务

```python
from typing import Protocol, AsyncIterator, Optional
from contextlib import asynccontextmanager

class IDatabase(Protocol):
    """数据库接口"""
    
    async def connect(self) -> None:
        """连接数据库"""
        ...
    
    async def disconnect(self) -> None:
        """断开连接"""
        ...
    
    @asynccontextmanager
    async def session(self) -> AsyncIterator:
        """获取会话"""
        ...
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        ...

class Database:
    """数据库实现（SQLAlchemy）"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._engine = None
        self._session_factory = None
    
    async def connect(self) -> None:
        """连接数据库"""
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        
        self._engine = create_async_engine(
            f"postgresql+asyncpg://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}",
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            echo=self.config.echo
        )
        
        self._session_factory = sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def disconnect(self) -> None:
        """断开连接"""
        if self._engine:
            await self._engine.dispose()
    
    @asynccontextmanager
    async def session(self) -> AsyncIterator:
        """获取会话"""
        if not self._session_factory:
            raise RuntimeError("Database not connected")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._engine is not None
```

## 二、缓存服务

```python
from typing import Protocol, Any, Optional
import json

class ICache(Protocol):
    """缓存接口"""
    
    async def get(self, key: str) -> Optional[Any]:
        """获取值"""
        ...
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """设置值"""
        ...
    
    async def delete(self, key: str) -> None:
        """删除值"""
        ...
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        ...

class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, config: RedisConfig):
        self.config = config
        self._client = None
    
    async def connect(self) -> None:
        """连接Redis"""
        import redis.asyncio as redis
        
        self._client = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            password=self.config.password,
            max_connections=self.config.max_connections
        )
    
    async def disconnect(self) -> None:
        """断开连接"""
        if self._client:
            await self._client.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取值"""
        value = await self._client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """设置值"""
        serialized = json.dumps(value)
        if ttl:
            await self._client.setex(key, ttl, serialized)
        else:
            await self._client.set(key, serialized)
    
    async def delete(self, key: str) -> None:
        """删除值"""
        await self._client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self._client.exists(key) > 0
```

## 三、LLM 客户端服务

```python
from typing import Protocol, Dict, Any, Optional
import time

class ILLMClient(Protocol):
    """LLM客户端接口"""
    
    async def complete(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """生成完成"""
        ...
    
    async def complete_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """带重试的完成"""
        ...

class LLMClient:
    """LLM客户端实现"""
    
    def __init__(
        self,
        config: LLMConfig,
        cache: Optional[ICache] = None
    ):
        self.config = config
        self.cache = cache
        self._client = None
    
    async def initialize(self) -> None:
        """初始化客户端"""
        if self.config.provider == "openai":
            self._client = OpenAIClient(self.config)
        elif self.config.provider == "anthropic":
            self._client = AnthropicClient(self.config)
        # ... 其他provider
    
    async def complete(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """生成完成"""
        if not self._client:
            await self.initialize()
        
        return await self._client.complete(
            prompt=prompt,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
    
    async def complete_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """带重试的完成"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await self.complete(prompt, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # 指数退避
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        raise last_error
```

## 四、健康检查服务

```python
from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import datetime

class HealthChecker:
    """健康检查器"""
    
    def __init__(
        self,
        database: IDatabase,
        cache: ICache,
        llm_client: ILLMClient
    ):
        self.database = database
        self.cache = cache
        self.llm_client = llm_client
        self._checks: Dict[str, callable] = {}
        self._register_checks()
    
    def _register_checks(self) -> None:
        """注册检查项"""
        self._checks["database"] = self._check_database
        self._checks["cache"] = self._check_cache
        self._checks["llm"] = self._check_llm
    
    async def check_all(self) -> "HealthReport":
        """执行所有检查"""
        results = {}
        
        for name, check_func in self._checks.items():
            try:
                results[name] = await check_func()
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "message": str(e)
                }
        
        overall_status = "healthy"
        if any(r.get("status") == "error" for r in results.values()):
            overall_status = "unhealthy"
        elif any(r.get("status") == "warning" for r in results.values()):
            overall_status = "degraded"
        
        return HealthReport(
            status=overall_status,
            checks=results,
            timestamp=datetime.now()
        )
    
    async def _check_database(self) -> Dict[str, Any]:
        """检查数据库"""
        if not self.database.is_connected:
            return {"status": "error", "message": "Database not connected"}
        
        try:
            async with self.database.session() as session:
                await session.execute("SELECT 1")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _check_cache(self) -> Dict[str, Any]:
        """检查缓存"""
        try:
            await self.cache.set("health_check", "ok", ttl=10)
            value = await self.cache.get("health_check")
            if value == "ok":
                return {"status": "healthy"}
            return {"status": "error", "message": "Cache read/write failed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _check_llm(self) -> Dict[str, Any]:
        """检查LLM"""
        try:
            # 简单的LLM调用测试
            await self.llm_client.complete("test")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "warning", "message": str(e)}

@dataclass
class HealthReport:
    """健康报告"""
    status: str  # healthy, degraded, unhealthy
    checks: Dict[str, Dict[str, Any]]
    timestamp: datetime
```

## 五、启动和关闭管理

```python
class AppLifecycle:
    """应用生命周期管理"""
    
    def __init__(self):
        self._started = False
        self._components: Dict[str, Any] = {}
    
    async def startup(self) -> None:
        """启动应用"""
        if self._started:
            return
        
        # 初始化配置
        config = load_config()
        
        # 初始化数据库
        database = Database(config.database)
        await database.connect()
        self._components["database"] = database
        
        # 初始化缓存
        cache = RedisCache(config.redis)
        await cache.connect()
        self._components["cache"] = cache
        
        # 初始化LLM客户端
        llm_client = LLMClient(config.llm, cache)
        await llm_client.initialize()
        self._components["llm"] = llm_client
        
        self._started = True
    
    async def shutdown(self) -> None:
        """关闭应用"""
        if not self._started:
            return
        
        # 按逆序关闭组件
        for name in ["llm", "cache", "database"]:
            component = self._components.get(name)
            if component and hasattr(component, "disconnect"):
                await component.disconnect()
        
        self._components.clear()
        self._started = False
```
