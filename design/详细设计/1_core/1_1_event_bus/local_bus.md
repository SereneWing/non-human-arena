# 本地事件总线实现

## 一、概述

LocalEventBus 是单进程内的事件总线实现，使用 asyncio 队列进行异步事件处理。

## 二、核心实现

```python
class LocalEventBus(EventBus):
    """本地事件总线"""
    
    def __init__(
        self,
        config: Optional[EventBusConfig] = None
    ):
        super().__init__()
        self.config = config or EventBusConfig()
        
        # 内部状态
        self._handlers: Dict[EventType, List[HandlerWrapper]] = defaultdict(list)
        self._once_handlers: Dict[EventType, List[HandlerWrapper]] = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.queue_size)
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        
        # 中间件
        self._middlewares: List[EventMiddleware] = []
        if self.config.enable_logging:
            self._middlewares.append(LoggingMiddleware())
        if self.config.enable_metrics:
            self._metrics = MetricsMiddleware()
            self._middlewares.append(self._metrics)
        
        # 错误策略
        self._error_strategy = self.config.error_strategy
    
    # ==================== 订阅管理 ====================
    
    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
        priority: int = 0
    ) -> None:
        """订阅事件"""
        wrapper = HandlerWrapper(
            handler=handler,
            is_async=asyncio.iscoroutinefunction(handler),
            priority=priority
        )
        
        handlers = self._handlers[event_type]
        handlers.append(wrapper)
        # 按优先级排序
        handlers.sort(key=lambda w: w.priority, reverse=True)
    
    def unsubscribe(
        self,
        event_type: EventType,
        handler: EventHandler
    ) -> None:
        """取消订阅"""
        handlers = self._handlers.get(event_type, [])
        self._handlers[event_type] = [
            w for w in handlers if w.handler != handler
        ]
    
    def subscribe_once(
        self,
        event_type: EventType,
        handler: EventHandler
    ) -> None:
        """单次订阅"""
        wrapper = HandlerWrapper(
            handler=handler,
            is_async=asyncio.iscoroutinefunction(handler),
            is_once=True
        )
        self._once_handlers[event_type].append(wrapper)
    
    def clear_subscriptions(self, event_type: EventType) -> None:
        """清除所有订阅"""
        self._handlers.pop(event_type, None)
        self._once_handlers.pop(event_type, None)
    
    def clear_all(self) -> None:
        """清除所有订阅"""
        self._handlers.clear()
        self._once_handlers.clear()
    
    # ==================== 发布管理 ====================
    
    async def publish(self, event: Event) -> None:
        """发布事件（异步）"""
        # 应用中间件
        for middleware in self._middlewares:
            event = await middleware.on_publish(event)
        
        # 入队
        try:
            await asyncio.wait_for(
                self._event_queue.put(event),
                timeout=self.config.queue_timeout
            )
        except asyncio.QueueFull:
            logger.warning(f"Event queue full, dropping event: {event.type}")
    
    def publish_sync(self, event: Event) -> None:
        """发布事件（同步，直接处理）"""
        # 应用中间件
        for middleware in self._middlewares:
            # 同步中间件可能需要处理
            if not asyncio.iscoroutinefunction(middleware.on_publish):
                event = middleware.on_publish(event)
            else:
                # 如果是异步中间件，创建任务但不等待
                asyncio.create_task(middleware.on_publish(event))
        
        # 直接处理事件
        asyncio.create_task(self._process_event(event))
    
    # ==================== 中间件 ====================
    
    def add_middleware(self, middleware: EventMiddleware) -> None:
        """添加中间件"""
        if middleware not in self._middlewares:
            self._middlewares.append(middleware)
    
    def remove_middleware(self, middleware: EventMiddleware) -> None:
        """移除中间件"""
        if middleware in self._middlewares:
            self._middlewares.remove(middleware)
    
    def get_middlewares(self) -> List[EventMiddleware]:
        """获取中间件列表"""
        return list(self._middlewares)
    
    # ==================== 生命周期 ====================
    
    async def start(self) -> None:
        """启动事件总线"""
        if self._running:
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._worker_loop())
        logger.info("LocalEventBus started")
    
    async def stop(self) -> None:
        """停止事件总线"""
        self._running = False
        
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        # 清空队列
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        logger.info("LocalEventBus stopped")
    
    # ==================== 工作循环 ====================
    
    async def _worker_loop(self) -> None:
        """事件处理工作循环"""
        while self._running:
            try:
                event = await self._event_queue.get()
                await self._process_event(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event worker loop: {e}")
    
    async def _process_event(self, event: Event) -> None:
        """处理单个事件"""
        # 处理常规订阅者
        handlers = self._handlers.get(event.type, [])
        for wrapper in handlers:
            await self._execute_handler(wrapper, event)
        
        # 处理单次订阅者
        once_handlers = self._once_handlers.get(event.type, [])
        for wrapper in once_handlers:
            await self._execute_handler(wrapper, event)
        # 清除已执行的单次订阅
        self._once_handlers[event.type] = []
    
    async def _execute_handler(
        self,
        wrapper: HandlerWrapper,
        event: Event
    ) -> None:
        """执行处理器"""
        try:
            if wrapper.is_async:
                await wrapper.handler(event)
            else:
                # 在异步上下文中运行同步处理器
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, wrapper.handler, event)
        except Exception as e:
            await self._handle_error(event, e, wrapper.handler)
    
    async def _handle_error(
        self,
        event: Event,
        error: Exception,
        handler: EventHandler
    ) -> None:
        """处理错误"""
        # 通知中间件
        for middleware in self._middlewares:
            try:
                if asyncio.iscoroutinefunction(middleware.on_error):
                    await middleware.on_error(event, error)
                else:
                    middleware.on_error(event, error)
            except Exception as e:
                logger.error(f"Error in middleware error handler: {e}")
        
        # 根据策略处理
        if self._error_strategy == EventErrorStrategy.THROW:
            raise error
        elif self._error_strategy == EventErrorStrategy.RETRY:
            await self._retry_handler(event, handler)
    
    async def _retry_handler(
        self,
        event: Event,
        handler: EventHandler
    ) -> None:
        """重试处理器"""
        for attempt in range(self.config.max_retries):
            try:
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                return
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise e
```

## 三、调度策略

```python
class DispatchStrategy(Enum):
    """事件调度策略"""
    SEQUENTIAL = "sequential"     # 顺序执行
    PARALLEL = "parallel"        # 并行执行
    FIRST_MATCH = "first_match"   # 只执行第一个
    
class LocalEventBusWithStrategy(LocalEventBus):
    """支持调度策略的事件总线"""
    
    def __init__(
        self,
        config: Optional[EventBusConfig] = None,
        strategy: DispatchStrategy = DispatchStrategy.SEQUENTIAL
    ):
        super().__init__(config)
        self.strategy = strategy
    
    async def _process_event(self, event: Event) -> None:
        """根据策略处理事件"""
        handlers = self._handlers.get(event.type, [])
        once_handlers = self._once_handlers.get(event.type, [])
        all_handlers = handlers + once_handlers
        
        if self.strategy == DispatchStrategy.SEQUENTIAL:
            for wrapper in all_handlers:
                await self._execute_handler(wrapper, event)
        elif self.strategy == DispatchStrategy.PARALLEL:
            await asyncio.gather(
                *[self._execute_handler(w, event) for w in all_handlers],
                return_exceptions=True
            )
        elif self.strategy == DispatchStrategy.FIRST_MATCH:
            if all_handlers:
                await self._execute_handler(all_handlers[0], event)
        
        # 清除单次订阅
        self._once_handlers[event.type] = []
```

## 四、通配符订阅

```python
class WildcardEventBus(LocalEventBus):
    """支持通配符订阅的事件总线"""
    
    def __init__(self, config: Optional[EventBusConfig] = None):
        super().__init__(config)
        self._wildcard_handlers: List[Tuple[str, HandlerWrapper]] = []
    
    def subscribe_wildcard(
        self,
        pattern: str,
        handler: EventHandler,
        priority: int = 0
    ) -> None:
        """
        通配符订阅
        
        pattern 例子:
        - "session.*" 匹配所有 session 相关事件
        - "*.created" 匹配所有 created 事件
        - "*" 匹配所有事件
        """
        wrapper = HandlerWrapper(
            handler=handler,
            is_async=asyncio.iscoroutinefunction(handler),
            priority=priority
        )
        self._wildcard_handlers.append((pattern, wrapper))
        # 按优先级排序
        self._wildcard_handlers.sort(key=lambda x: x[1].priority, reverse=True)
    
    def _matches_pattern(self, event_type: EventType, pattern: str) -> bool:
        """检查事件类型是否匹配模式"""
        if pattern == "*":
            return True
        
        event_str = event_type.value
        
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_str.startswith(prefix + ".")
        elif pattern.startswith("*."):
            suffix = pattern[2:]
            return event_str.endswith(suffix)
        else:
            return event_str == pattern
    
    async def _process_event(self, event: Event) -> None:
        """处理事件（包括通配符匹配）"""
        # 处理常规订阅
        await super()._process_event(event)
        
        # 处理通配符订阅
        for pattern, wrapper in self._wildcard_handlers:
            if self._matches_pattern(event.type, pattern):
                await self._execute_handler(wrapper, event)
```

## 五、会话隔离

```python
class SessionIsolatedEventBus(LocalEventBus):
    """支持会话隔离的事件总线"""
    
    def __init__(self, config: Optional[EventBusConfig] = None):
        super().__init__(config)
        self._session_handlers: Dict[str, Dict[EventType, List[HandlerWrapper]]] = defaultdict(list)
        self._global_handlers: Dict[EventType, List[HandlerWrapper]] = dict(self._handlers)
    
    def subscribe_session(
        self,
        session_id: str,
        event_type: EventType,
        handler: EventHandler,
        priority: int = 0
    ) -> None:
        """订阅会话特定事件"""
        wrapper = HandlerWrapper(
            handler=handler,
            is_async=asyncio.iscoroutinefunction(handler),
            priority=priority
        )
        handlers = self._session_handlers[session_id][event_type]
        handlers.append(wrapper)
        handlers.sort(key=lambda w: w.priority, reverse=True)
    
    def unsubscribe_session(
        self,
        session_id: str,
        event_type: EventType,
        handler: EventHandler
    ) -> None:
        """取消会话特定订阅"""
        if session_id not in self._session_handlers:
            return
        
        handlers = self._session_handlers[session_id].get(event_type, [])
        self._session_handlers[session_id][event_type] = [
            w for w in handlers if w.handler != handler
        ]
    
    def clear_session(self, session_id: str) -> None:
        """清除会话所有订阅"""
        self._session_handlers.pop(session_id, None)
    
    async def _process_event(self, event: Event) -> None:
        """处理事件（会话隔离）"""
        # 处理全局订阅
        await super()._process_event(event)
        
        # 处理会话特定订阅
        if event.session_id and event.session_id in self._session_handlers:
            handlers = self._session_handlers[event.session_id].get(event.type, [])
            for wrapper in handlers:
                await self._execute_handler(wrapper, event)
```

## 六、性能优化

```python
class OptimizedEventBus(LocalEventBus):
    """优化的事件总线"""
    
    def __init__(self, config: Optional[EventBusConfig] = None):
        super().__init__(config)
        
        # 批量处理
        self._batch_size = 10
        self._batch_timeout = 0.01  # 10ms
        self._pending_events: List[Event] = []
        self._batch_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """启动（带批量处理）"""
        await super().start()
        self._batch_task = asyncio.create_task(self._batch_processor())
    
    async def stop(self) -> None:
        """停止"""
        if self._batch_task:
            self._batch_task.cancel()
        await super().stop()
    
    async def _batch_processor(self) -> None:
        """批量处理器"""
        while self._running:
            await asyncio.sleep(self._batch_timeout)
            
            if self._pending_events:
                batch = self._pending_events[:self._batch_size]
                self._pending_events = self._pending_events[self._batch_size:]
                
                for event in batch:
                    await self._process_event(event)
    
    async def publish(self, event: Event) -> None:
        """发布事件（批量优化）"""
        for middleware in self._middlewares:
            event = await middleware.on_publish(event)
        
        self._pending_events.append(event)
```

## 七、使用示例

```python
# 基本用法
event_bus = LocalEventBus()
await event_bus.start()

async def on_message(event):
    print(f"收到消息: {event.data}")

event_bus.subscribe(EventType.MESSAGE_RECEIVED, on_message)
await event_bus.publish(Event(
    type=EventType.MESSAGE_RECEIVED,
    source="test",
    data={"content": "hello"}
))

await event_bus.stop()

# 通配符用法
event_bus = WildcardEventBus()
event_bus.subscribe_wildcard("session.*", on_session_event)
event_bus.subscribe_wildcard("*.created", on_created_event)

# 会话隔离用法
event_bus = SessionIsolatedEventBus()
event_bus.subscribe_session("session_1", EventType.MESSAGE_RECEIVED, handler1)
event_bus.subscribe_session("session_2", EventType.MESSAGE_RECEIVED, handler2)
```
