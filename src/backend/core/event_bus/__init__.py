"""Event Bus implementation."""
from __future__ import annotations

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger(__name__)

EventHandler = Callable[[Event], Optional[Any]]
EventHandlerAsync = Callable[[Event], Any]


class EventType(Enum):
    """System event types."""
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_STARTED = "session.started"
    SESSION_PAUSED = "session.paused"
    SESSION_RESUMED = "session.resumed"
    SESSION_ENDED = "session.ended"
    SESSION_ERROR = "session.error"
    
    # Message events
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    MESSAGE_PROCESSED = "message.processed"
    
    # AI events
    AI_THINKING = "ai.thinking"
    AI_SPOKE = "ai.spoke"
    AI_SKIP = "ai.skip"
    AI_ACT = "ai.act"
    AI_HEARTBEAT = "ai.heartbeat"
    
    # Role events
    ROLE_CREATED = "role.created"
    ROLE_UPDATED = "role.updated"
    ROLE_DELETED = "role.deleted"
    
    # Rule events
    RULE_TRIGGERED = "rule.triggered"
    RULE_VIOLATED = "rule.violated"
    RULE_CONSEQUENCE_EXECUTED = "rule.consequence.executed"
    
    # Heartbeat events
    HEARTBEAT_TICK = "heartbeat.tick"
    HEARTBEAT_TIMEOUT = "heartbeat.timeout"
    
    # Error events
    ERROR = "error"


@dataclass
class Event:
    """Base event class."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.SYSTEM_STARTUP
    source: str = ""
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    
    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()


@dataclass
class HandlerWrapper:
    """Event handler wrapper."""
    
    handler: EventHandler
    is_async: bool = False
    is_once: bool = False
    priority: int = 0
    subscriber_name: str = "anonymous"


class EventBus(ABC):
    """Abstract event bus base class."""
    
    def __init__(self) -> None:
        self._handlers: Dict[EventType, List[HandlerWrapper]] = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
    
    @abstractmethod
    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
        subscriber_name: str = "anonymous",
        priority: int = 0,
    ) -> None:
        """Subscribe to an event."""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: EventType, subscriber_name: str) -> None:
        """Unsubscribe from an event."""
        pass
    
    @abstractmethod
    def subscribe_once(
        self,
        event_type: EventType,
        handler: EventHandler,
        subscriber_name: str = "anonymous",
    ) -> None:
        """Subscribe to an event once."""
        pass
    
    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish an event (async)."""
        pass
    
    @abstractmethod
    def publish_sync(self, event: Event) -> None:
        """Publish an event (sync)."""
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Start the event bus."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the event bus."""
        pass
    
    def get_handler_count(self, event_type: EventType) -> int:
        """Get handler count for an event type."""
        return len(self._handlers.get(event_type, []))
    
    def get_all_subscriptions(self) -> Dict[EventType, int]:
        """Get all subscriptions."""
        return {etype: len(handlers) for etype, handlers in self._handlers.items()}


class LocalEventBus(EventBus):
    """Local in-process event bus."""
    
    def __init__(self) -> None:
        super().__init__()
        self._task: Optional[asyncio.Task] = None
    
    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
        subscriber_name: str = "anonymous",
        priority: int = 0,
    ) -> None:
        """Subscribe to an event."""
        is_async = asyncio.iscoroutinefunction(handler)
        wrapper = HandlerWrapper(
            handler=handler,
            is_async=is_async,
            is_once=False,
            priority=priority,
            subscriber_name=subscriber_name,
        )
        self._handlers[event_type].append(wrapper)
        self._handlers[event_type].sort(key=lambda w: w.priority, reverse=True)
        logger.debug(f"Subscribed {subscriber_name} to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, subscriber_name: str) -> None:
        """Unsubscribe from an event."""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                wrapper
                for wrapper in self._handlers[event_type]
                if wrapper.subscriber_name != subscriber_name
            ]
            logger.debug(f"Unsubscribed {subscriber_name} from {event_type.value}")
    
    def subscribe_once(
        self,
        event_type: EventType,
        handler: EventHandler,
        subscriber_name: str = "anonymous",
    ) -> None:
        """Subscribe to an event once."""
        is_async = asyncio.iscoroutinefunction(handler)
        wrapper = HandlerWrapper(
            handler=handler,
            is_async=is_async,
            is_once=True,
            priority=0,
            subscriber_name=subscriber_name,
        )
        self._handlers[event_type].append(wrapper)
        logger.debug(f"Subscribed {subscriber_name} to {event_type.value} (once)")
    
    async def publish(self, event: Event) -> None:
        """Publish an event asynchronously."""
        event_type = event.type
        logger.debug(f"Publishing event: {event_type.value} from {event.source}")
        
        if event_type not in self._handlers:
            return
        
        handlers_to_remove: List[HandlerWrapper] = []
        
        for wrapper in self._handlers[event_type]:
            try:
                if wrapper.is_async:
                    await wrapper.handler(event)
                else:
                    wrapper.handler(event)
                
                if wrapper.is_once:
                    handlers_to_remove.append(wrapper)
                    
            except Exception as e:
                logger.error(
                    f"Error handling event {event_type.value} "
                    f"in {wrapper.subscriber_name}: {e}"
                )
        
        for wrapper in handlers_to_remove:
            self._handlers[event_type].remove(wrapper)
    
    def publish_sync(self, event: Event) -> None:
        """Publish an event synchronously."""
        event_type = event.type
        logger.debug(f"Publishing event (sync): {event_type.value} from {event.source}")
        
        if event_type not in self._handlers:
            return
        
        handlers_to_remove: List[HandlerWrapper] = []
        
        for wrapper in self._handlers[event_type]:
            try:
                if wrapper.is_async:
                    logger.warning(
                        f"Async handler called synchronously for {event_type.value}"
                    )
                else:
                    wrapper.handler(event)
                
                if wrapper.is_once:
                    handlers_to_remove.append(wrapper)
                    
            except Exception as e:
                logger.error(
                    f"Error handling event {event_type.value} "
                    f"in {wrapper.subscriber_name}: {e}"
                )
        
        for wrapper in handlers_to_remove:
            self._handlers[event_type].remove(wrapper)
    
    async def start(self) -> None:
        """Start the event bus."""
        if self._running:
            return
        self._running = True
        logger.info("Event bus started")
    
    async def stop(self) -> None:
        """Stop the event bus."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Event bus stopped")


_event_bus: Optional[LocalEventBus] = None


def get_event_bus() -> LocalEventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = LocalEventBus()
    return _event_bus


def set_event_bus(event_bus: LocalEventBus) -> None:
    """Set the global event bus instance."""
    global _event_bus
    _event_bus = event_bus
