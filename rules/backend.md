# 后端编码规范

## 一、代码风格

### 1.1 基础规范

- **使用类型注解**：所有函数参数和返回值必须标注类型
- **使用 Pydantic**：数据验证和序列化使用 Pydantic v2
- **异步优先**：IO 操作必须使用 async/await
- **PEP 8 规范**：遵循 Python 代码风格指南
- **类型检查**：使用 mypy 进行静态类型检查

### 1.2 缩进与格式

- **缩进**：使用 4 空格
- **行长限制**：最大 120 字符
- **导入排序**：标准库 → 第三方库 → 本地模块
- **空行使用**：顶级定义之间两个空行，方法之间一个空行

```python
# ✅ 正确
def get_user_by_id(user_id: str) -> User | None:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()


class UserService:
    """用户服务"""
    
    def __init__(self, repository: IUserRepository):
        self.repository = repository
    
    async def get_user(self, user_id: str) -> User | None:
        """获取用户"""
        return await self.repository.get_by_id(user_id)
```

### 1.3 命名规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 模块 | snake_case | `user_repository.py` |
| 类 | PascalCase | `UserService`, `BaseModel` |
| 函数 | snake_case | `get_user_by_id`, `create_session` |
| 变量 | snake_case | `user_id`, `session_list` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 类型别名 | PascalCase | `UserId`, `SessionStatus` |
| 枚举值 | UPPER_SNAKE_CASE | `SessionStatus.RUNNING` |
| 私有属性 | _snake_case | `_internal_cache` |

### 1.4 类型注解

```python
from typing import TypeVar, Generic, Protocol, Optional
from pydantic import BaseModel

T = TypeVar('T')
UserId = str
SessionId = str

# ✅ 使用 Pydantic BaseModel
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

# ✅ 使用 Protocol 定义接口
class IUserRepository(Protocol):
    async def get_by_id(self, user_id: str) -> Optional[User]: ...
    async def create(self, user: UserCreate) -> User: ...
    async def delete(self, user_id: str) -> bool: ...

# ✅ 使用泛型
class ResponseWrapper(BaseModel, Generic[T]):
    success: bool
    data: T
    message: str | None = None
```

## 二、项目结构

```
src/
├── api/                    # API 路由层
│   ├── __init__.py
│   ├── deps.py             # 依赖注入
│   ├── roles.py            # 角色路由
│   ├── rules.py            # 规则路由
│   └── sessions.py         # 会话路由
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库连接
│   └── event_bus.py        # 事件总线
├── models/                 # 数据模型 (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py
│   ├── role.py
│   ├── rule.py
│   └── session.py
├── schemas/                # Pydantic schemas
│   ├── __init__.py
│   ├── role.py
│   ├── rule.py
│   └── session.py
├── repositories/           # 数据访问层
│   ├── __init__.py
│   ├── role_repository.py
│   ├── rule_repository.py
│   └── session_repository.py
├── services/               # 业务逻辑层
│   ├── __init__.py
│   ├── role_service.py
│   ├── rule_service.py
│   ├── session_service.py
│   └── ai_service.py
├── events/                 # 事件定义
│   ├── __init__.py
│   ├── base.py
│   ├── role_events.py
│   ├── session_events.py
│   └── handlers.py
├── llm/                    # LLM 适配器
│   ├── __init__.py
│   ├── base.py
│   ├── openai_adapter.py
│   └── anthropic_adapter.py
├── utils/                  # 工具函数
│   ├── __init__.py
│   ├── security.py
│   └── validators.py
└── main.py                 # 应用入口
```

## 三、API 层规范

### 3.1 路由定义

```python
# api/roles.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.role import RoleCreate, RoleUpdate, RoleResponse
from services.role_service import RoleService
from api.deps import get_role_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    service: RoleService = Depends(get_role_service)
) -> List[RoleResponse]:
    """获取角色列表"""
    roles = await service.get_roles(skip=skip, limit=limit)
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    service: RoleService = Depends(get_role_service)
) -> RoleResponse:
    """获取单个角色"""
    role = await service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    service: RoleService = Depends(get_role_service)
) -> RoleResponse:
    """创建角色"""
    return await service.create_role(role_data)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    service: RoleService = Depends(get_role_service)
) -> RoleResponse:
    """更新角色"""
    role = await service.update_role(role_id, role_data)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    service: RoleService = Depends(get_role_service)
) -> None:
    """删除角色"""
    deleted = await service.delete_role(role_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
```

### 3.2 依赖注入

```python
# api/deps.py
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from repositories.role_repository import RoleRepository
from repositories.session_repository import SessionRepository
from services.role_service import RoleService
from services.session_service import SessionService


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    return get_db()


@lru_cache
def get_role_repository() -> RoleRepository:
    """获取角色仓储"""
    return RoleRepository()


@lru_cache
def get_session_repository() -> SessionRepository:
    """获取会话仓储"""
    return SessionRepository()


async def get_role_service(
    repository: RoleRepository = Depends(get_role_repository)
) -> RoleService:
    """获取角色服务"""
    return RoleService(repository)


async def get_session_service(
    repository: SessionRepository = Depends(get_session_repository)
) -> SessionService:
    """获取会话服务"""
    return SessionService(repository)
```

### 3.3 错误处理

```python
# api/exceptions.py
from fastapi import HTTPException, status

class AppException(HTTPException):
    """应用异常基类"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str | None = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class NotFoundError(AppException):
    """资源不存在"""
    
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{resource_id}' not found",
            code="NOT_FOUND"
        )


class ValidationError(AppException):
    """验证错误"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code="VALIDATION_ERROR"
        )


class UnauthorizedError(AppException):
    """未授权"""
    
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="UNAUTHORIZED"
        )
```

## 四、数据模型 (Pydantic Schemas)

### 4.1 Schema 组织

```python
# schemas/role.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class RoleBase(BaseModel):
    """角色基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    personality: dict = Field(default_factory=dict)


class RoleCreate(RoleBase):
    """创建角色"""
    prompt_template: str = Field(..., min_length=1)


class RoleUpdate(BaseModel):
    """更新角色"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    personality: Optional[dict] = None
    prompt_template: Optional[str] = Field(None, min_length=1)


class RoleResponse(RoleBase):
    """角色响应"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

### 4.2 嵌套 Schema

```python
# schemas/session.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from schemas.role import RoleResponse

class SessionBase(BaseModel):
    """会话基础 Schema"""
    topic: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None


class SessionCreate(SessionBase):
    """创建会话"""
    role_ids: List[str] = Field(..., min_length=2)
    settings: dict = Field(default_factory=dict)


class SessionResponse(SessionBase):
    """会话响应"""
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SessionDetailResponse(SessionResponse):
    """会话详情响应"""
    roles: List[RoleResponse] = []
    message_count: int = 0


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    session_id: str
    role_id: str
    role_name: str
    content: str
    mental_activity: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

## 五、数据模型 (SQLAlchemy)

### 5.1 模型定义

```python
# models/base.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """基础模型类"""
    pass


class TimestampMixin:
    """时间戳混入"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UUIDMixin:
    """UUID 主键混入"""
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )
```

### 5.2 具体模型

```python
# models/role.py
from uuid import uuid4
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from models.base import Base, TimestampMixin, UUIDMixin


class Role(Base, UUIDMixin, TimestampMixin):
    """角色模型"""
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    personality: Mapped[dict] = mapped_column(JSON, default_factory=dict)
    
    # 关系
    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="role",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
```

## 六、仓储层 (Repository)

### 6.1 仓储接口

```python
# repositories/base.py
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.base import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """基础仓储类（不管理事务）"""
    
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """根据ID获取"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, obj: T) -> T:
        """创建（事务由 Database.session() 管理）"""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, obj: T) -> T:
        """更新（事务由 Database.session() 管理）"""
        await self.session.flush()
        await self.session.refresh(obj)
        return obj
    
    async def delete(self, obj: T) -> bool:
        """删除（事务由 Database.session() 管理）"""
        await self.session.delete(obj)
        await self.session.flush()
        return True
```

### 6.2 具体仓储

```python
# repositories/role_repository.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate

class RoleRepository:
    """角色仓储（不管理事务，由调用方通过 Database.session() 管理）"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """根据ID获取角色"""
        result = await self.session.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取所有角色"""
        result = await self.session.execute(
            select(Role).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, data: RoleCreate) -> Role:
        """创建角色（事务由 Database.session() 管理）"""
        role = Role(
            name=data.name,
            description=data.description,
            prompt_template=data.prompt_template,
            personality=data.personality or {}
        )
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return role
    
    async def update(self, role_id: str, data: RoleUpdate) -> Optional[Role]:
        """更新角色（事务由 Database.session() 管理）"""
        role = await self.get_by_id(role_id)
        if not role:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(role, key, value)
        
        await self.session.flush()
        await self.session.refresh(role)
        return role
    
    async def delete(self, role_id: str) -> bool:
        """删除角色（事务由 Database.session() 管理）"""
        role = await self.get_by_id(role_id)
        if not role:
            return False
        await self.session.delete(role)
        await self.session.flush()
        return True
```

### 6.3 仓储使用（配合 Database Context Manager）

```python
# services/role_service.py（使用示例）
from typing import List, Optional
from databases import Database
from repositories.role_repository import RoleRepository
from schemas.role import RoleCreate, RoleUpdate, RoleResponse

class RoleService:
    """角色服务"""
    
    def __init__(self, database: Database, repository: RoleRepository):
        self.database = database
        self.repository = repository
    
    async def get_roles(self, skip: int = 0, limit: int = 100) -> List[RoleResponse]:
        """获取角色列表"""
        async with self.database.session() as session:
            repository = RoleRepository(session)
            roles = await repository.get_all(skip=skip, limit=limit)
            return [RoleResponse.model_validate(role) for role in roles]
    
    async def get_role_by_id(self, role_id: str) -> Optional[RoleResponse]:
        """根据ID获取角色"""
        async with self.database.session() as session:
            repository = RoleRepository(session)
            role = await repository.get_by_id(role_id)
            if not role:
                return None
            return RoleResponse.model_validate(role)
    
    async def create_role(self, data: RoleCreate) -> RoleResponse:
        """创建角色"""
        async with self.database.session() as session:
            repository = RoleRepository(session)
            role = await repository.create(data)
            return RoleResponse.model_validate(role)
    
    async def update_role(self, role_id: str, data: RoleUpdate) -> Optional[RoleResponse]:
        """更新角色"""
        async with self.database.session() as session:
            repository = RoleRepository(session)
            role = await repository.update(role_id, data)
            if not role:
                return None
            return RoleResponse.model_validate(role)
    
    async def delete_role(self, role_id: str) -> bool:
        """删除角色"""
        async with self.database.session() as session:
            repository = RoleRepository(session)
            return await repository.delete(role_id)
```

## 七、服务层 (Service)

### 7.1 服务定义

```python
# services/role_service.py
from typing import List, Optional
from repositories.role_repository import RoleRepository
from schemas.role import RoleCreate, RoleUpdate, RoleResponse


class RoleService:
    """角色服务"""
    
    def __init__(self, repository: RoleRepository):
        self.repository = repository
    
    async def get_roles(self, skip: int = 0, limit: int = 100) -> List[RoleResponse]:
        """获取角色列表"""
        roles = await self.repository.get_all(skip=skip, limit=limit)
        return [RoleResponse.model_validate(role) for role in roles]
    
    async def get_role_by_id(self, role_id: str) -> Optional[RoleResponse]:
        """根据ID获取角色"""
        role = await self.repository.get_by_id(role_id)
        if not role:
            return None
        return RoleResponse.model_validate(role)
    
    async def create_role(self, data: RoleCreate) -> RoleResponse:
        """创建角色"""
        role = await self.repository.create(data)
        return RoleResponse.model_validate(role)
    
    async def update_role(self, role_id: str, data: RoleUpdate) -> Optional[RoleResponse]:
        """更新角色"""
        role = await self.repository.update(role_id, data)
        if not role:
            return None
        return RoleResponse.model_validate(role)
    
    async def delete_role(self, role_id: str) -> bool:
        """删除角色"""
        return await self.repository.delete(role_id)
```

## 八、事件系统

### 8.1 事件定义

```python
# events/base.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import uuid


@dataclass
class BaseEvent:
    """事件基类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


@dataclass
class RoleCreatedEvent(BaseEvent):
    """角色创建事件"""
    role_id: str
    name: str
    created_by: Optional[str] = None


@dataclass
class SessionStartedEvent(BaseEvent):
    """会话开始事件"""
    session_id: str
    topic: str
    participant_ids: list[str]


@dataclass
class MessageSentEvent(BaseEvent):
    """消息发送事件"""
    session_id: str
    message_id: str
    role_id: str
    content: str
```

### 8.2 事件总线

```python
# core/event_bus.py
from typing import Callable, Dict, List, Type
from dataclasses import dataclass
from events.base import BaseEvent
import logging

logger = logging.getLogger(__name__)

EventHandler = Callable[[BaseEvent], None]


@dataclass
class Subscription:
    """事件订阅"""
    event_type: Type[BaseEvent]
    handler: EventHandler
    subscriber_name: str


class EventBus:
    """事件总线"""
    
    def __init__(self):
        self._handlers: Dict[Type[BaseEvent], List[Subscription]] = {}
    
    def subscribe(
        self,
        event_type: Type[BaseEvent],
        handler: EventHandler,
        subscriber_name: str = "anonymous"
    ) -> None:
        """订阅事件"""
        subscription = Subscription(event_type, handler, subscriber_name)
        
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(subscription)
        logger.debug(f"Subscribed {subscriber_name} to {event_type.__name__}")
    
    def unsubscribe(self, event_type: Type[BaseEvent], subscriber_name: str) -> None:
        """取消订阅"""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                sub for sub in self._handlers[event_type]
                if sub.subscriber_name != subscriber_name
            ]
    
    async def publish(self, event: BaseEvent) -> None:
        """发布事件"""
        event_type = type(event)
        
        if event_type not in self._handlers:
            logger.debug(f"No handlers for event {event_type.__name__}")
            return
        
        for subscription in self._handlers[event_type]:
            try:
                await subscription.handler(event)
            except Exception as e:
                logger.error(
                    f"Error handling event {event_type.__name__} "
                    f"in {subscription.subscriber_name}: {e}"
                )


# 全局事件总线实例
event_bus = EventBus()
```

### 8.3 事件处理器

```python
# events/handlers.py
from events.base import RoleCreatedEvent, SessionStartedEvent
from core.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)


async def on_role_created(event: RoleCreatedEvent) -> None:
    """角色创建事件处理"""
    logger.info(f"Role created: {event.name} (id: {event.role_id})")
    # 执行后续逻辑，如发送通知等


async def on_session_started(event: SessionStartedEvent) -> None:
    """会话开始事件处理"""
    logger.info(f"Session started: {event.topic}")
    # 初始化会话上下文等


# 注册处理器
def register_handlers() -> None:
    """注册所有事件处理器"""
    event_bus.subscribe(RoleCreatedEvent, on_role_created, "role_handler")
    event_bus.subscribe(SessionStartedEvent, on_session_started, "session_handler")
```

## 九、异步处理

### 9.1 异步数据库操作

```python
# core/database.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool

DATABASE_URL = "sqlite+aiosqlite:///./data.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool  # SQLite 不支持连接池
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db() -> AsyncSession:
    """同步获取会话（用于 FastAPI 依赖注入）"""
    return AsyncSessionLocal()
```

### 9.2 异步任务

```python
# services/ai_service.py
import asyncio
from typing import AsyncGenerator


class AIService:
    """AI 服务"""
    
    def __init__(self, adapter: "LLMAdapter"):
        self.adapter = adapter
    
    async def generate_response(
        self,
        prompt: str,
        context: list[dict]
    ) -> str:
        """生成响应"""
        messages = [
            {"role": "system", "content": prompt},
            *context
        ]
        
        response = await self.adapter.chat(messages)
        return response
    
    async def stream_generate(
        self,
        prompt: str,
        context: list[dict]
    ) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        messages = [
            {"role": "system", "content": prompt},
            *context
        ]
        
        async for chunk in self.adapter.stream_chat(messages):
            yield chunk
```

## 十、日志与监控

### 10.1 日志配置

```python
# core/logging.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_level: str = "INFO") -> None:
    """配置日志"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                log_dir / "app.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

### 10.2 结构化日志

```python
# 使用结构化日志
import structlog

logger = structlog.get_logger()

logger.info(
    "session_created",
    session_id="123",
    topic="AI的未来",
    participant_count=3
)

logger.error(
    "message_generation_failed",
    error="timeout",
    session_id="123",
    role_id="456"
)
```

## 十一、测试规范

### 11.1 测试组织

```
tests/
├── conftest.py              # pytest 配置
├── fixtures/
│   ├── __init__.py
│   ├── user_fixtures.py
│   └── session_fixtures.py
├── api/
│   ├── __init__.py
│   ├── test_roles.py
│   └── test_sessions.py
├── services/
│   ├── __init__.py
│   ├── test_role_service.py
│   └── test_session_service.py
└── repositories/
    ├── __init__.py
    └── test_role_repository.py
```

### 11.2 单元测试示例

```python
# tests/services/test_role_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from services.role_service import RoleService
from schemas.role import RoleCreate, RoleResponse


class TestRoleService:
    
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def service(self, mock_repository):
        return RoleService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_create_role(self, service, mock_repository):
        # Arrange
        role_data = RoleCreate(
            name="Test Role",
            description="A test role",
            prompt_template="You are a test role"
        )
        
        mock_repository.create.return_value = MagicMock(
            id="123",
            name="Test Role",
            description="A test role",
            prompt_template="You are a test role",
            personality={}
        )
        
        # Act
        result = await service.create_role(role_data)
        
        # Assert
        assert result.name == "Test Role"
        assert result.id == "123"
        mock_repository.create.assert_called_once()
```

## 十二、Git 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
perf: 性能优化
test: 测试
chore: 构建/工具变更
```

示例：
```
feat(session): 添加会话创建和启动功能
fix(role): 修复角色列表查询性能问题
docs(api): 更新 REST API 文档
refactor(event): 重构事件总线实现
test(service): 添加角色服务单元测试
```
