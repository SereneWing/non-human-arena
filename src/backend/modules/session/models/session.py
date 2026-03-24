"""Session SQLAlchemy models."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base


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


class SessionModel(Base):
    """Session database model."""
    
    __tablename__ = "sessions"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(Text, nullable=False, default="")
    state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=SessionState.CREATED.value,
    )
    template_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Role IDs as JSON array
    role_ids: Mapped[List[str]] = mapped_column(JSON, default_factory=list)
    
    # Configuration
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Creator
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Relationships
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    participants: Mapped[List["ParticipantModel"]] = relationship(
        "ParticipantModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<SessionModel(id={self.id}, name={self.name}, state={self.state})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "topic": self.topic,
            "state": self.state,
            "template_id": self.template_id,
            "role_ids": self.role_ids,
            "config": self.config,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_by": self.created_by,
        }


class MessageModel(Base):
    """Message database model."""
    
    __tablename__ = "messages"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participant_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=True,
    )
    role_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Message content
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="text")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    mental_activity: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Message metadata
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    
    # Relationships
    session: Mapped["SessionModel"] = relationship(
        "SessionModel",
        back_populates="messages",
    )
    role: Mapped[Optional["RoleModel"]] = relationship(
        "RoleModel",
        back_populates="messages",
    )
    participant: Mapped[Optional["ParticipantModel"]] = relationship(
        "ParticipantModel",
        back_populates="messages",
    )
    
    def __repr__(self) -> str:
        return f"<MessageModel(id={self.id}, session_id={self.session_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "role_id": self.role_id,
            "type": self.type,
            "content": self.content,
            "mental_activity": self.mental_activity,
            "turn_number": self.turn_number,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ParticipantModel(Base):
    """Participant database model."""
    
    __tablename__ = "participants"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Participant info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_ai: Mapped[bool] = mapped_column(default=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    # Relationships
    session: Mapped["SessionModel"] = relationship(
        "SessionModel",
        back_populates="participants",
    )
    role: Mapped["RoleModel"] = relationship(
        "RoleModel",
        back_populates="participants",
    )
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="participant",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<ParticipantModel(id={self.id}, name={self.name})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role_id": self.role_id,
            "name": self.name,
            "is_ai": self.is_ai,
            "is_active": self.is_active,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None,
            "metadata": self.metadata,
        }


# Import RoleModel at bottom to avoid circular imports
from modules.role.models.role import RoleModel
