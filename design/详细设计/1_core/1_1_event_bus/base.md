# 事件总线基类设计

## 一、概述

EventBus 是系统核心通信机制，提供模块间的异步事件发布-订阅功能。

## 二、Event 基类

```python
@dataclass
class Event:
    """事件基类"""
    id: str                      # 事件唯一ID
    type: EventType              # 事件类型
    source: str                  # 事件来源模块
    session_id: Optional[str]    # 会话ID（如果有）
    timestamp: datetime          # 事件时间戳
    data: Dict[str, Any]         # 事件数据
    correlation_id: Optional[str] # 关联ID（用于追踪）
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()
```

## 三、EventBus 抽象基类

```python
class EventBus(ABC):
    """事件总线抽象基类"""
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._middlewares: List[EventMiddleware] = []
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
    
    # ==================== 订阅管理 ====================
    
    @abstractmethod
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """订阅事件"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """取消订阅"""
        pass
    
    @abstractmethod
    def subscribe_once(self, event_type: EventType, handler: EventHandler) -> None:
        """单次订阅（触发一次后自动取消）"""
        pass
    
    # ==================== 发布管理 ====================
    
    @abstractmethod
    async def publish(self, event: Event) -> None:
        """发布事件（异步）"""
        pass
    
    @abstractmethod
    def publish_sync(self, event: Event) -> None:
        """发布事件（同步）"""
        pass
    
    # ==================== 中间件 ====================
    
    @abstractmethod
    def add_middleware(self, middleware: EventMiddleware) -> None:
        """添加中间件"""
        pass
    
    @abstractmethod
    def remove_middleware(self, middleware: EventMiddleware) -> None:
        """移除中间件"""
        pass
    
    # ==================== 生命周期 ====================
    
    @abstractmethod
    async def start(self) -> None:
        """启动事件总线"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """停止事件总线"""
        pass
    
    # ==================== 工具方法 ====================
    
    def get_handler_count(self, event_type: EventType) -> int:
        """获取处理器数量"""
        return len(self._handlers.get(event_type, []))
    
    def get_all_subscriptions(self) -> Dict[EventType, int]:
        """获取所有订阅"""
        return {etype: len(handlers) for etype, handlers in self._handlers.items()}
```

## 四、EventHandler 类型

```python
# 事件处理器类型定义
EventHandler = Callable[[Event], Optional[Awaitable[Any]]]
EventHandlerSync = Callable[[Event], Optional[Any]]

# 处理器包装器
@dataclass
class HandlerWrapper:
    """处理器包装器"""
    handler: EventHandler
    is_async: bool
    is_once: bool = False  # 是否单次执行
    priority: int = 0       # 优先级（数字越大越先执行）
```

## 五、中间件接口

```python
class EventMiddleware(ABC):
    """事件中间件抽象基类"""
    
    @abstractmethod
    async def on_publish(self, event: Event) -> Event:
        """发布前拦截"""
        pass
    
    @abstractmethod
    async def on_subscribe(self, event_type: EventType, handler: EventHandler) -> EventHandler:
        """订阅前拦截"""
        pass
    
    @abstractmethod
    async def on_error(self, event: Event, error: Exception) -> None:
        """错误处理"""
        pass

# 内置中间件
class LoggingMiddleware(EventMiddleware):
    """日志中间件"""
    
    async def on_publish(self, event: Event) -> Event:
        logger.debug(f"Publishing event: {event.type} from {event.source}")
        return event
    
    async def on_subscribe(self, event_type: EventType, handler: EventHandler) -> EventHandler:
        logger.debug(f"Subscribing to event: {event_type}")
        return handler
    
    async def on_error(self, event: Event, error: Exception) -> None:
        logger.error(f"Event error: {event.type} - {error}")

class MetricsMiddleware(EventMiddleware):
    """指标中间件"""
    
    def __init__(self):
        self.event_counts: Dict[EventType, int] = defaultdict(int)
        self.error_counts: Dict[EventType, int] = defaultdict(int)
        self.latencies: Dict[EventType, List[float]] = defaultdict(list)
    
    async def on_publish(self, event: Event) -> Event:
        self.event_counts[event.type] += 1
        return event
    
    async def on_subscribe(self, event_type: EventType, handler: EventHandler) -> EventHandler:
        return handler
    
    async def on_error(self, event: Event, error: Exception) -> None:
        self.error_counts[event.type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "event_counts": dict(self.event_counts),
            "error_counts": dict(self.error_counts)
        }
```

## 六、事件处理器注册装饰器

```python
def event_handler(event_type: EventType, priority: int = 0):
    """事件处理器装饰器"""
    def decorator(func: EventHandler):
        func._event_type = event_type
        func._priority = priority
        return func
    return decorator

# 使用示例
class MyComponent:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._register_handlers()
    
    def _register_handlers(self):
        # 自动注册带装饰器的方法
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_event_type'):
                self.event_bus.subscribe(
                    attr._event_type,
                    attr,
                    priority=attr._priority
                )
    
    @event_handler(EventType.MESSAGE_RECEIVED, priority=10)
    async def handle_message(self, event: Event):
        print(f"Received: {event.data}")
```

## 七、错误处理策略

```python
class EventErrorStrategy(Enum):
    """事件错误处理策略"""
    THROW = "throw"              # 抛出异常
    LOG = "log"                  # 仅记录日志
    RETRY = "retry"             # 重试
    FALLBACK = "fallback"       # 执行备用处理器
    IGNORE = "ignore"           # 忽略

@dataclass
class EventErrorConfig:
    """错误配置"""
    strategy: EventErrorStrategy = EventErrorStrategy.LOG
    max_retries: int = 3
    retry_delay: float = 1.0
    fallback_handler: Optional[EventHandler] = None
```

## 八、订阅者优先级

```python
class Priority:
    """处理器优先级常量"""
    SYSTEM = 100   # 系统级处理器
    CORE = 80      # 核心模块
    HIGH = 60      # 高优先级
    NORMAL = 40   # 普通
    LOW = 20      # 低优先级
    BACKGROUND = 0  # 后台任务
```

## 九、类型安全

```python
# 泛型事件处理器
T = TypeVar('T', bound=Event)

class TypedEventHandler(Generic[T], Protocol):
    """类型化事件处理器"""
    async def __call__(self, event: T) -> None: ...

# 类型化订阅
def subscribe_typed(
    event_bus: EventBus,
    event_type: Type[T],
    handler: TypedEventHandler[T]
) -> None:
    """类型化订阅"""
    async def wrapper(event: Event):
        if isinstance(event, event_type):
            await handler(event)
    event_bus.subscribe(event_type, wrapper)
```

## 十、配置选项

```python
@dataclass
class EventBusConfig:
    """事件总线配置"""
    # 队列配置
    queue_size: int = 1000
    queue_timeout: float = 5.0
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # 错误处理
    error_strategy: EventErrorStrategy = EventErrorStrategy.LOG
    
    # 性能配置
    enable_metrics: bool = True
    enable_logging: bool = True
    
    # 分布式配置
    enable_broadcast: bool = False
    broadcast_timeout: float = 10.0
```
