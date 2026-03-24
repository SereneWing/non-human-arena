# 心跳模块服务层

## 一、心跳引擎接口

```python
from typing import Protocol, Dict, Any, Optional
from datetime import datetime

class IHeartbeatEngine(Protocol):
    """心跳引擎接口"""
    
    async def start(self, session_id: str) -> None:
        """启动心跳"""
        ...
    
    async def stop(self, session_id: str) -> None:
        """停止心跳"""
        ...
    
    async def pause(self, session_id: str) -> None:
        """暂停心跳"""
        ...
    
    async def resume(self, session_id: str) -> None:
        """恢复心跳"""
        ...
    
    async def tick(self, session_id: str) -> None:
        """执行一次心跳"""
        ...
    
    def get_status(self, session_id: str) -> "HeartbeatStatus":
        """获取心跳状态"""
        ...

@dataclass
class HeartbeatStatus:
    """心跳状态"""
    session_id: str
    is_running: bool
    is_paused: bool
    last_tick: Optional[datetime]
    tick_count: int
    missed_heartbeats: int
```

## 二、心跳引擎实现

```python
import asyncio
from typing import Dict, Optional
from datetime import datetime

class HeartbeatEngine:
    """心跳引擎实现"""
    
    def __init__(
        self,
        event_bus: IEventBus,
        session_repository: ISessionRepository,
        config: HeartbeatConfig
    ):
        self.event_bus = event_bus
        self.session_repository = session_repository
        self.config = config
        self._sessions: Dict[str, HeartbeatSession] = {}
    
    async def start(self, session_id: str) -> None:
        """启动心跳"""
        if session_id in self._sessions:
            return
        
        session = HeartbeatSession(
            session_id=session_id,
            interval=self.config.interval,
            timeout=self.config.timeout,
            event_bus=self.event_bus
        )
        
        self._sessions[session_id] = session
        await session.start()
        
        # 发布心跳启动事件
        await self.event_bus.publish(Event(
            type=EventType.HEARTBEAT_TICK,
            source="heartbeat_engine",
            session_id=session_id,
            data={"action": "start"}
        ))
    
    async def stop(self, session_id: str) -> None:
        """停止心跳"""
        if session_id not in self._sessions:
            return
        
        session = self._sessions.pop(session_id)
        await session.stop()
        
        # 发布心跳停止事件
        await self.event_bus.publish(Event(
            type=EventType.HEARTBEAT_TICK,
            source="heartbeat_engine",
            session_id=session_id,
            data={"action": "stop"}
        ))
    
    async def pause(self, session_id: str) -> None:
        """暂停心跳"""
        if session_id in self._sessions:
            await self._sessions[session_id].pause()
    
    async def resume(self, session_id: str) -> None:
        """恢复心跳"""
        if session_id in self._sessions:
            await self._sessions[session_id].resume()
    
    def get_status(self, session_id: str) -> Optional[HeartbeatStatus]:
        """获取心跳状态"""
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        return HeartbeatStatus(
            session_id=session_id,
            is_running=session.is_running,
            is_paused=session.is_paused,
            last_tick=session.last_tick,
            tick_count=session.tick_count,
            missed_heartbeats=session.missed_heartbeats
        )

@dataclass
class HeartbeatConfig:
    """心跳配置"""
    interval: float = 1.0              # 心跳间隔（秒）
    timeout: float = 10.0              # 超时时间（秒）
    max_missed: int = 3               # 最大允许错过次数
    enable_ai_heartbeat: bool = True   # 启用AI心跳

class HeartbeatSession:
    """心跳会话"""
    
    def __init__(
        self,
        session_id: str,
        interval: float,
        timeout: float,
        event_bus: IEventBus
    ):
        self.session_id = session_id
        self.interval = interval
        self.timeout = timeout
        self.event_bus = event_bus
        self.is_running = False
        self.is_paused = False
        self.last_tick: Optional[datetime] = None
        self.tick_count = 0
        self.missed_heartbeats = 0
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """启动心跳"""
        if self.is_running:
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._heartbeat_loop())
    
    async def stop(self) -> None:
        """停止心跳"""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def pause(self) -> None:
        """暂停心跳"""
        self.is_paused = True
    
    async def resume(self) -> None:
        """恢复心跳"""
        self.is_paused = False
    
    async def _heartbeat_loop(self) -> None:
        """心跳循环"""
        while self.is_running:
            if not self.is_paused:
                await self._tick()
            
            await asyncio.sleep(self.interval)
    
    async def _tick(self) -> None:
        """执行一次心跳"""
        self.last_tick = datetime.now()
        self.tick_count += 1
        
        # 发布心跳事件
        await self.event_bus.publish(Event(
            type=EventType.HEARTBEAT_TICK,
            source="heartbeat_session",
            session_id=self.session_id,
            data={
                "tick_count": self.tick_count,
                "timestamp": self.last_tick.isoformat()
            }
        ))
        
        # 检查超时
        await self._check_timeout()
    
    async def _check_timeout(self) -> None:
        """检查超时"""
        if self.last_tick:
            elapsed = (datetime.now() - self.last_tick).total_seconds()
            if elapsed > self.timeout:
                self.missed_heartbeats += 1
                
                # 发布超时事件
                await self.event_bus.publish(Event(
                    type=EventType.ERROR,
                    source="heartbeat_engine",
                    session_id=self.session_id,
                    data={
                        "error": "heartbeat_timeout",
                        "missed_heartbeats": self.missed_heartbeats,
                        "last_tick": self.last_tick.isoformat()
                    }
                ))
                
                if self.missed_heartbeats >= 3:
                    # 发布会话超时事件
                    await self.event_bus.publish(Event(
                        type=EventType.SESSION_ERROR,
                        source="heartbeat_engine",
                        session_id=self.session_id,
                        data={"reason": "heartbeat_timeout"}
                    ))
```

## 三、与AI引擎的集成

```python
class AIHeartbeatMonitor:
    """AI心跳监控"""
    
    def __init__(
        self,
        event_bus: IEventBus,
        ai_engine: IAIEngine,
        config: AIHeartbeatConfig
    ):
        self.event_bus = event_bus
        self.ai_engine = ai_engine
        self.config = config
        self._last_activity: Dict[str, datetime] = {}
        self._subscribed = False
    
    async def start(self) -> None:
        """启动监控"""
        if not self._subscribed:
            self.event_bus.subscribe(
                EventType.AI_ACT,
                self._on_ai_activity
            )
            self.event_bus.subscribe(
                EventType.AI_SKIP,
                self._on_ai_activity
            )
            self._subscribed = True
    
    async def _on_ai_activity(self, event: Event) -> None:
        """AI活动处理"""
        participant_id = event.data.get("participant_id")
        if participant_id:
            self._last_activity[participant_id] = datetime.now()
    
    async def check_ai_timeout(
        self,
        session_id: str,
        participant_id: str
    ) -> bool:
        """检查AI是否超时"""
        if participant_id not in self._last_activity:
            return False
        
        elapsed = (datetime.now() - self._last_activity[participant_id]).total_seconds()
        return elapsed > self.config.ai_timeout
```

## 四、配置说明

```python
# 心跳配置示例
heartbeat_config = HeartbeatConfig(
    interval=1.0,           # 每秒一次心跳
    timeout=10.0,           # 10秒超时
    max_missed=3,           # 最多允许3次心跳丢失
    enable_ai_heartbeat=True # 启用AI心跳
)

# AI心跳配置
ai_heartbeat_config = AIHeartbeatConfig(
    ai_timeout=30.0,       # AI响应超时30秒
    max_retries=2,         # 最多重试2次
    recovery_enabled=True    # 启用自动恢复
)
```
