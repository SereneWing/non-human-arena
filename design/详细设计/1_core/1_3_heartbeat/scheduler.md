# 心跳调度器设计

## 一、概述

HeartbeatScheduler 负责管理所有会话的心跳任务，支持自适应调节和动态优先级。

## 二、调度器核心

```python
class HeartbeatScheduler:
    """心跳调度器"""
    
    def __init__(
        self,
        event_bus: EventBus,
        config: Optional[HeartbeatConfig] = None
    ):
        self.event_bus = event_bus
        self.config = config or HeartbeatConfig()
        
        # 心跳任务管理
        self._tasks: Dict[str, asyncio.Task] = {}  # session_id -> task
        self._timers: Dict[str, float] = {}  # session_id -> last_tick
        self._priorities: Dict[str, int] = {}  # session_id -> priority
        
        # 调度策略
        self._strategy = self._create_strategy()
        
        # 统计
        self._stats: Dict[str, HeartbeatStats] = defaultdict(HeartbeatStats)
        
        # 生命周期
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        
        # 订阅事件
        self._setup_subscriptions()
    
    def _create_strategy(self) -> SchedulingStrategy:
        """创建调度策略"""
        if self.config.policy == HeartbeatPolicy.ADAPTIVE:
            return AdaptiveStrategy(self.config)
        elif self.config.policy == HeartbeatPolicy.FIXED_RATE:
            return FixedRateStrategy(self.config)
        elif self.config.policy == HeartbeatPolicy.DEADLINE:
            return DeadlineStrategy(self.config)
        else:
            return PriorityStrategy(self.config)
    
    def _setup_subscriptions(self):
        """订阅事件"""
        self.event_bus.subscribe(EventType.SESSION_STARTED, self._on_session_started)
        self.event_bus.subscribe(EventType.SESSION_ENDED, self._on_session_ended)
        self.event_bus.subscribe(EventType.SESSION_PAUSED, self._on_session_paused)
        self.event_bus.subscribe(EventType.SESSION_RESUMED, self._on_session_resumed)
```

## 三、调度策略接口

```python
class SchedulingStrategy(ABC):
    """调度策略抽象基类"""
    
    def __init__(self, config: HeartbeatConfig):
        self.config = config
    
    @abstractmethod
    def get_next_tick(self, session_id: str) -> float:
        """获取下次tick时间戳"""
        pass
    
    @abstractmethod
    def calculate_priority(self, session_id: str) -> int:
        """计算优先级"""
        pass
    
    @abstractmethod
    def should_skip(self, session_id: str) -> bool:
        """是否应该跳过本次tick"""
        pass

class FixedRateStrategy(SchedulingStrategy):
    """固定速率策略"""
    
    def get_next_tick(self, session_id: str) -> float:
        return time.time() + self.config.interval
    
    def calculate_priority(self, session_id: str) -> int:
        return Priority.NORMAL
    
    def should_skip(self, session_id: str) -> bool:
        return False

class AdaptiveStrategy(SchedulingStrategy):
    """自适应策略"""
    
    def __init__(self, config: HeartbeatConfig):
        super().__init__(config)
        self._activity_scores: Dict[str, float] = defaultdict(lambda: 0.5)
        self._last_activity: Dict[str, float] = {}
    
    def get_next_tick(self, session_id: str) -> float:
        """根据活动评分动态调整间隔"""
        score = self._activity_scores.get(session_id, 0.5)
        
        # 活跃度高 -> 缩短间隔
        # 活跃度低 -> 延长间隔
        interval = self.config.interval * (1.5 - score)
        interval = max(self.config.min_interval, min(self.config.max_interval, interval))
        
        return time.time() + interval
    
    def calculate_priority(self, session_id: str) -> int:
        score = self._activity_scores.get(session_id, 0.5)
        return int(score * Priority.HIGH + (1 - score) * Priority.LOW)
    
    def should_skip(self, session_id: str) -> bool:
        """检查是否应该跳过"""
        last = self._last_activity.get(session_id, 0)
        elapsed = time.time() - last
        
        # 长时间无活动则跳过
        if elapsed > self.config.max_idle_time:
            return True
        
        # 活动评分低于阈值则延长间隔
        if self._activity_scores[session_id] < 0.2:
            return True
        
        return False
    
    def update_activity(self, session_id: str, activity: float):
        """更新活动评分"""
        # 指数移动平均
        current = self._activity_scores[session_id]
        self._activity_scores[session_id] = 0.7 * current + 0.3 * activity
        self._last_activity[session_id] = time.time()
```

## 四、会话管理

```python
    # ==================== 会话管理 ====================
    
    async def register_session(
        self,
        session_id: str,
        config: Optional[SessionHeartbeatConfig] = None
    ) -> None:
        """注册会话"""
        if session_id in self._tasks:
            logger.warning(f"Session {session_id} already registered")
            return
        
        session_config = config or SessionHeartbeatConfig()
        self._priorities[session_id] = session_config.priority
        
        # 创建心跳任务
        task = asyncio.create_task(self._heartbeat_loop(session_id, session_config))
        self._tasks[session_id] = task
        
        logger.info(f"Registered heartbeat for session {session_id}")
    
    async def unregister_session(self, session_id: str) -> None:
        """取消注册会话"""
        if session_id not in self._tasks:
            return
        
        # 取消任务
        task = self._tasks.pop(session_id)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # 清理数据
        self._timers.pop(session_id, None)
        self._priorities.pop(session_id, None)
        
        logger.info(f"Unregistered heartbeat for session {session_id}")
    
    async def pause_session(self, session_id: str) -> None:
        """暂停会话心跳"""
        if session_id in self._tasks:
            self._tasks[session_id].cancel()
            try:
                await self._tasks[session_id]
            except asyncio.CancelledError:
                pass
            del self._tasks[session_id]
    
    async def resume_session(self, session_id: str) -> None:
        """恢复会话心跳"""
        if session_id in self._tasks and session_id not in self._tasks:
            await self.register_session(session_id)
```

## 五、心跳循环

```python
    async def _heartbeat_loop(
        self,
        session_id: str,
        config: SessionHeartbeatConfig
    ) -> None:
        """心跳主循环"""
        logger.debug(f"Heartbeat loop started for {session_id}")
        
        try:
            while True:
                # 检查是否应该跳过
                if self._strategy.should_skip(session_id):
                    await self._wait_for_next_tick(session_id)
                    continue
                
                # 记录tick时间
                tick_time = time.time()
                self._timers[session_id] = tick_time
                
                # 发布心跳事件
                await self._send_heartbeat(session_id, tick_time)
                
                # 更新统计
                self._update_stats(session_id, tick_time)
                
                # 等待下次tick
                await self._wait_for_next_tick(session_id)
                
        except asyncio.CancelledError:
            logger.debug(f"Heartbeat loop cancelled for {session_id}")
            raise
        except Exception as e:
            logger.error(f"Heartbeat loop error for {session_id}: {e}")
            # 发布错误事件
            await self.event_bus.publish(Event(
                type=EventType.ERROR,
                source="heartbeat_scheduler",
                session_id=session_id,
                data={"error": str(e), "component": "heartbeat_loop"}
            ))
    
    async def _wait_for_next_tick(self, session_id: str) -> None:
        """等待下次tick"""
        next_tick = self._strategy.get_next_tick(session_id)
        wait_time = max(0, next_tick - time.time())
        
        try:
            await asyncio.sleep(wait_time)
        except asyncio.CancelledError:
            raise
    
    async def _send_heartbeat(self, session_id: str, tick_time: float) -> None:
        """发送心跳事件"""
        await self.event_bus.publish(Event(
            type=EventType.HEARTBEAT_TICK,
            source="heartbeat_scheduler",
            session_id=session_id,
            data={
                "timestamp": tick_time,
                "priority": self._priorities.get(session_id, Priority.NORMAL)
            }
        ))
```

## 六、统计与监控

```python
@dataclass
class HeartbeatStats:
    """心跳统计"""
    total_ticks: int = 0
    missed_ticks: int = 0
    skipped_ticks: int = 0
    avg_latency: float = 0.0
    last_tick_time: float = 0.0
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_ticks": self.total_ticks,
            "missed_ticks": self.missed_ticks,
            "skipped_ticks": self.skipped_ticks,
            "avg_latency_ms": self.avg_latency * 1000,
            "last_tick_time": self.last_tick_time,
            "last_error": self.last_error
        }

class HeartbeatMonitor:
    """心跳监控"""
    
    def __init__(self, scheduler: HeartbeatScheduler):
        self.scheduler = scheduler
        self._monitors: Dict[str, Callable] = {}
    
    def register_monitor(
        self,
        session_id: str,
        callback: Callable[[HeartbeatStats], None]
    ) -> None:
        """注册监控回调"""
        self._monitors[session_id] = callback
    
    def get_stats(self, session_id: str) -> Optional[HeartbeatStats]:
        """获取统计信息"""
        return self.scheduler._stats.get(session_id)
    
    def get_all_stats(self) -> Dict[str, HeartbeatStats]:
        """获取所有统计"""
        return dict(self.scheduler._stats)
    
    def is_healthy(self, session_id: str) -> bool:
        """检查会话心跳健康状态"""
        stats = self.get_stats(session_id)
        if not stats:
            return False
        
        # 检查是否有最近的tick
        if time.time() - stats.last_tick_time > 60:
            return False
        
        # 检查错误率
        if stats.total_ticks > 0:
            error_rate = stats.missed_ticks / stats.total_ticks
            if error_rate > 0.1:  # 10% 错误率阈值
                return False
        
        return True
    
    def get_unhealthy_sessions(self) -> List[str]:
        """获取不健康的会话列表"""
        return [
            session_id for session_id in self.scheduler._tasks.keys()
            if not self.is_healthy(session_id)
        ]
```

## 七、生命周期管理

```python
    # ==================== 生命周期 ====================
    
    async def start(self) -> None:
        """启动调度器"""
        if self._running:
            return
        
        self._running = True
        self._main_task = asyncio.create_task(self._maintenance_loop())
        
        logger.info("HeartbeatScheduler started")
    
    async def stop(self) -> None:
        """停止调度器"""
        self._running = False
        
        # 取消所有任务
        for task in self._tasks.values():
            task.cancel()
        
        # 等待任务结束
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()
        
        # 停止维护循环
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass
        
        logger.info("HeartbeatScheduler stopped")
    
    async def _maintenance_loop(self) -> None:
        """维护循环"""
        while self._running:
            try:
                # 检查超时会话
                await self._check_timeouts()
                
                # 重新调度失败的任务
                await self._reschedule_failed()
                
                # 等待下次维护
                await asyncio.sleep(10)  # 每10秒维护一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Maintenance loop error: {e}")
    
    async def _check_timeouts(self) -> None:
        """检查超时"""
        now = time.time()
        timeout = self.config.session_timeout
        
        for session_id, last_tick in list(self._timers.items()):
            if now - last_tick > timeout:
                logger.warning(f"Session {session_id} heartbeat timeout")
                await self.event_bus.publish(Event(
                    type=EventType.ERROR,
                    source="heartbeat_scheduler",
                    session_id=session_id,
                    data={"error": "heartbeat_timeout"}
                ))
    
    async def _reschedule_failed(self) -> None:
        """重新调度失败的任务"""
        for session_id, task in list(self._tasks.items()):
            if task.done() and not task.cancelled():
                exc = task.exception()
                if exc:
                    logger.error(f"Rescheduling failed task for {session_id}: {exc}")
                    # 重新创建任务
                    new_task = asyncio.create_task(
                        self._heartbeat_loop(session_id, SessionHeartbeatConfig())
                    )
                    self._tasks[session_id] = new_task
```

## 八、事件处理

```python
    async def _on_session_started(self, event: Event) -> None:
        """处理会话开始事件"""
        session_id = event.session_id
        session_config = event.data.get("heartbeat_config")
        
        await self.register_session(session_id, session_config)
    
    async def _on_session_ended(self, event: Event) -> None:
        """处理会话结束事件"""
        session_id = event.session_id
        await self.unregister_session(session_id)
    
    async def _on_session_paused(self, event: Event) -> None:
        """处理会话暂停事件"""
        session_id = event.session_id
        await self.pause_session(session_id)
    
    async def _on_session_resumed(self, event: Event) -> None:
        """处理会话恢复事件"""
        session_id = event.session_id
        await self.resume_session(session_id)
```

## 九、配置选项

```python
@dataclass
class SessionHeartbeatConfig:
    """会话心跳配置"""
    interval: float = 5.0           # 心跳间隔（秒）
    priority: int = Priority.NORMAL # 优先级
    enable_adaptive: bool = True     # 是否启用自适应
    timeout: float = 30.0           # 超时时间
```

## 十、使用示例

```python
# 基本用法
scheduler = HeartbeatScheduler(event_bus, config)
await scheduler.start()

# 注册会话
await scheduler.register_session("session_123")

# 监控心跳
monitor = HeartbeatMonitor(scheduler)
stats = monitor.get_stats("session_123")
print(f"Ticks: {stats.total_ticks}, Missed: {stats.missed_ticks}")

# 健康检查
if monitor.is_healthy("session_123"):
    print("Session is healthy")
else:
    print("Session is unhealthy")

# 获取所有不健康会话
unhealthy = monitor.get_unhealthy_sessions()

await scheduler.stop()
```
