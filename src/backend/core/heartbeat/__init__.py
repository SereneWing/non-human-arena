"""Heartbeat Engine - AI proactive thinking and speaking scheduler."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from core.event_bus import Event, EventBus, EventType

logger = logging.getLogger(__name__)


@dataclass
class HeartbeatConfig:
    """Heartbeat engine configuration."""
    
    interval: float = 1.0
    timeout: float = 10.0
    max_missed: int = 3
    enable_ai_heartbeat: bool = True


@dataclass
class HeartbeatStatus:
    """Heartbeat status."""
    
    session_id: str
    is_running: bool = False
    is_paused: bool = False
    last_tick: Optional[datetime] = None
    tick_count: int = 0
    missed_heartbeats: int = 0


@dataclass
class HeartbeatSession:
    """Heartbeat session."""
    
    session_id: str
    interval: float
    timeout: float
    event_bus: EventBus
    is_running: bool = False
    is_paused: bool = False
    last_tick: Optional[datetime] = None
    tick_count: int = 0
    missed_heartbeats: int = 0
    _task: Optional[asyncio.Task] = None


@dataclass
class HeartbeatTickEvent:
    """Heartbeat tick event data."""
    
    action: str = "tick"
    tick_count: int = 0
    timestamp: Optional[datetime] = None


class HeartbeatEngine:
    """Heartbeat engine for AI proactive thinking."""
    
    def __init__(
        self,
        event_bus: EventBus,
        config: Optional[HeartbeatConfig] = None,
    ) -> None:
        self.event_bus = event_bus
        self.config = config or HeartbeatConfig()
        self._sessions: Dict[str, HeartbeatSession] = {}
    
    async def start(self, session_id: str) -> None:
        """Start heartbeat for a session."""
        if session_id in self._sessions:
            return
        
        session = HeartbeatSession(
            session_id=session_id,
            interval=self.config.interval,
            timeout=self.config.timeout,
            event_bus=self.event_bus,
        )
        
        self._sessions[session_id] = session
        await session.start()
        
        await self.event_bus.publish(Event(
            type=EventType.HEARTBEAT_TICK,
            source="heartbeat_engine",
            session_id=session_id,
            data={"action": "start", "tick_count": 0},
        ))
        
        logger.info(f"Heartbeat started for session: {session_id}")
    
    async def stop(self, session_id: str) -> None:
        """Stop heartbeat for a session."""
        if session_id not in self._sessions:
            return
        
        session = self._sessions.pop(session_id)
        await session.stop()
        
        await self.event_bus.publish(Event(
            type=EventType.HEARTBEAT_TICK,
            source="heartbeat_engine",
            session_id=session_id,
            data={"action": "stop"},
        ))
        
        logger.info(f"Heartbeat stopped for session: {session_id}")
    
    async def pause(self, session_id: str) -> None:
        """Pause heartbeat for a session."""
        if session_id in self._sessions:
            await self._sessions[session_id].pause()
            logger.info(f"Heartbeat paused for session: {session_id}")
    
    async def resume(self, session_id: str) -> None:
        """Resume heartbeat for a session."""
        if session_id in self._sessions:
            await self._sessions[session_id].resume()
            logger.info(f"Heartbeat resumed for session: {session_id}")
    
    async def tick(self, session_id: str) -> None:
        """Execute a single heartbeat tick."""
        if session_id in self._sessions:
            await self._sessions[session_id].tick()
    
    def get_status(self, session_id: str) -> Optional[HeartbeatStatus]:
        """Get heartbeat status for a session."""
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        return HeartbeatStatus(
            session_id=session_id,
            is_running=session.is_running,
            is_paused=session.is_paused,
            last_tick=session.last_tick,
            tick_count=session.tick_count,
            missed_heartbeats=session.missed_heartbeats,
        )
    
    def get_all_status(self) -> Dict[str, HeartbeatStatus]:
        """Get heartbeat status for all sessions."""
        return {
            session_id: self.get_status(session_id)
            for session_id in self._sessions
        }


class HeartbeatSession:
    """Heartbeat session implementation."""
    
    def __init__(
        self,
        session_id: str,
        interval: float,
        timeout: float,
        event_bus: EventBus,
    ) -> None:
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
        """Start the heartbeat session."""
        if self.is_running:
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._heartbeat_loop())
    
    async def stop(self) -> None:
        """Stop the heartbeat session."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def pause(self) -> None:
        """Pause the heartbeat."""
        self.is_paused = True
    
    async def resume(self) -> None:
        """Resume the heartbeat."""
        self.is_paused = False
    
    async def tick(self) -> None:
        """Execute a single tick."""
        self.last_tick = datetime.now()
        self.tick_count += 1
        
        await self.event_bus.publish(Event(
            type=EventType.HEARTBEAT_TICK,
            source="heartbeat_session",
            session_id=self.session_id,
            data={
                "tick_count": self.tick_count,
                "timestamp": self.last_tick.isoformat(),
            },
        ))
        
        await self._check_timeout()
    
    async def _heartbeat_loop(self) -> None:
        """Heartbeat loop."""
        while self.is_running:
            if not self.is_paused:
                await self.tick()
            
            await asyncio.sleep(self.interval)
    
    async def _check_timeout(self) -> None:
        """Check for timeout."""
        if self.last_tick:
            elapsed = (datetime.now() - self.last_tick).total_seconds()
            if elapsed > self.timeout:
                self.missed_heartbeats += 1
                
                await self.event_bus.publish(Event(
                    type=EventType.ERROR,
                    source="heartbeat_engine",
                    session_id=self.session_id,
                    data={
                        "error": "heartbeat_timeout",
                        "missed_heartbeats": self.missed_heartbeats,
                        "last_tick": self.last_tick.isoformat(),
                    },
                ))
                
                if self.missed_heartbeats >= 3:
                    await self.event_bus.publish(Event(
                        type=EventType.SESSION_ERROR,
                        source="heartbeat_engine",
                        session_id=self.session_id,
                        data={"reason": "heartbeat_timeout"},
                    ))


_heartbeat_engine: Optional[HeartbeatEngine] = None


def get_heartbeat_engine() -> HeartbeatEngine:
    """Get the global heartbeat engine instance."""
    global _heartbeat_engine
    if _heartbeat_engine is None:
        _heartbeat_engine = HeartbeatEngine(get_event_bus())
    return _heartbeat_engine


def set_heartbeat_engine(engine: HeartbeatEngine) -> None:
    """Set the global heartbeat engine instance."""
    global _heartbeat_engine
    _heartbeat_engine = engine
