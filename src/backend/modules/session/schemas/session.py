"""Session Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SessionState(str, Enum):
    """Session state enumeration."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    WAITING = "waiting"
    RUNNING = "running"
    PAUSED = "paused"
    ENDING = "ending"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class SessionBase(BaseModel):
    """Session base schema."""
    
    name: str = Field(..., min_length=1, max_length=200)
    topic: str = Field(default="", max_length=1000)
    template_id: Optional[str] = None


class SessionCreate(SessionBase):
    """Session creation schema."""
    
    role_ids: List[str] = Field(..., min_length=1)
    config: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionUpdate(BaseModel):
    """Session update schema."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    topic: Optional[str] = Field(None, max_length=1000)
    state: Optional[SessionState] = None
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(SessionBase):
    """Session response schema."""
    
    id: str
    state: SessionState
    role_ids: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MessageBase(BaseModel):
    """Message base schema."""
    
    type: str = Field(default="text")
    content: str = Field(..., min_length=1)
    mental_activity: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageCreate(MessageBase):
    """Message creation schema."""
    
    participant_id: Optional[str] = None
    role_id: Optional[str] = None


class MessageResponse(MessageBase):
    """Message response schema."""
    
    id: str
    session_id: str
    participant_id: Optional[str] = None
    role_id: Optional[str] = None
    turn_number: int = 0
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ParticipantBase(BaseModel):
    """Participant base schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    is_ai: bool = Field(default=True)


class ParticipantCreate(ParticipantBase):
    """Participant creation schema."""
    
    role_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParticipantResponse(ParticipantBase):
    """Participant response schema."""
    
    id: str
    session_id: str
    role_id: str
    is_active: bool
    joined_at: datetime
    left_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class SessionDetailResponse(SessionResponse):
    """Session detail response with participants and message count."""
    
    participants: List[ParticipantResponse] = Field(default_factory=list)
    message_count: int = 0


class SessionListResponse(BaseModel):
    """Session list response schema."""
    
    items: List[SessionResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class StateTransitionRequest(BaseModel):
    """State transition request schema."""
    
    target_state: SessionState
    reason: Optional[str] = None


class StateTransitionResponse(BaseModel):
    """State transition response schema."""
    
    success: bool
    from_state: SessionState
    to_state: SessionState
    message: Optional[str] = None
