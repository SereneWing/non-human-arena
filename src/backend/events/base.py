"""Base event definitions."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class BaseEvent:
    """Base event class."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "event_type": self.__class__.__name__,
        }


@dataclass
class RoleCreatedEvent(BaseEvent):
    """Role created event."""
    
    role_id: str = ""
    name: str = ""
    category: str = ""
    created_by: Optional[str] = None


@dataclass
class RoleUpdatedEvent(BaseEvent):
    """Role updated event."""
    
    role_id: str = ""
    name: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoleDeletedEvent(BaseEvent):
    """Role deleted event."""
    
    role_id: str = ""
    name: str = ""


@dataclass
class SessionCreatedEvent(BaseEvent):
    """Session created event."""
    
    session_id: str = ""
    name: str = ""
    topic: str = ""
    participant_ids: List[str] = field(default_factory=list)


@dataclass
class SessionStartedEvent(BaseEvent):
    """Session started event."""
    
    session_id: str = ""
    topic: str = ""
    participant_ids: List[str] = field(default_factory=list)


@dataclass
class SessionPausedEvent(BaseEvent):
    """Session paused event."""
    
    session_id: str = ""
    reason: Optional[str] = None


@dataclass
class SessionResumedEvent(BaseEvent):
    """Session resumed event."""
    
    session_id: str = ""


@dataclass
class SessionEndedEvent(BaseEvent):
    """Session ended event."""
    
    session_id: str = ""
    reason: Optional[str] = None
    duration: Optional[float] = None


@dataclass
class SessionErrorEvent(BaseEvent):
    """Session error event."""
    
    session_id: str = ""
    error: str = ""
    details: Optional[Dict[str, Any]] = None


@dataclass
class MessageReceivedEvent(BaseEvent):
    """Message received event."""
    
    session_id: str = ""
    message_id: str = ""
    participant_id: str = ""
    content: str = ""


@dataclass
class MessageSentEvent(BaseEvent):
    """Message sent event."""
    
    session_id: str = ""
    message_id: str = ""
    participant_id: str = ""
    content: str = ""
    mental_activity: Optional[str] = None


@dataclass
class AIThinkingEvent(BaseEvent):
    """AI thinking event."""
    
    session_id: str = ""
    participant_id: str = ""
    thinking: str = ""


@dataclass
class AISpokeEvent(BaseEvent):
    """AI spoke event."""
    
    session_id: str = ""
    participant_id: str = ""
    content: str = ""
    confidence: float = 1.0


@dataclass
class AISkipEvent(BaseEvent):
    """AI skip event."""
    
    session_id: str = ""
    participant_id: str = ""
    reason: Optional[str] = None
