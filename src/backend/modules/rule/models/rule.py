"""Rule SQLAlchemy models."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class RuleType(str, Enum):
    """Rule type enumeration."""
    
    DEBATE = "debate"
    GAME = "game"
    NEGOTIATION = "negotiation"
    TEACHING = "teaching"
    ROLEPLAY = "roleplay"
    CUSTOM = "custom"


class ConstraintType(str, Enum):
    """Constraint type enumeration."""
    
    MESSAGE_LENGTH = "message_length"
    WORD_COUNT = "word_count"
    KEYWORD_REQUIRED = "keyword_required"
    KEYWORD_FORBIDDEN = "keyword_forbidden"
    TIMING = "timing"
    CUSTOM = "custom"


class TriggerType(str, Enum):
    """Trigger type enumeration."""
    
    EVENT = "event"
    CONDITION = "condition"
    TIMER = "timer"


class ConsequenceType(str, Enum):
    """Consequence type enumeration."""
    
    SEND_MESSAGE = "send_message"
    MODIFY_BEHAVIOR = "modify_behavior"
    APPLY_PENALTY = "apply_penalty"
    END_SESSION = "end_session"
    SKIP_TURN = "skip_turn"
    CUSTOM = "custom"


class RuleModel(Base):
    """Rule database model."""
    
    __tablename__ = "rules"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default=RuleType.DEBATE.value)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Constraints as JSON
    constraints: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default_factory=list)
    
    # Triggers as JSON
    triggers: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default_factory=list)
    
    # Consequences as JSON
    consequences: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default_factory=list)
    
    # Enabled flag
    enabled: Mapped[bool] = mapped_column(default=True)
    
    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    
    def __repr__(self) -> str:
        return f"<RuleModel(id={self.id}, name={self.name})>"


class ConstraintModel(Base):
    """Constraint database model."""
    
    __tablename__ = "constraints"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rule_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    target: Mapped[str] = mapped_column(String(100), nullable=False, default="participant")
    condition: Mapped[str] = mapped_column(Text, nullable=False, default="")
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    priority: Mapped[int] = mapped_column(default=0)
    
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    def __repr__(self) -> str:
        return f"<ConstraintModel(id={self.id}, type={self.type})>"


class TriggerModel(Base):
    """Trigger database model."""
    
    __tablename__ = "triggers"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rule_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    condition: Mapped[str] = mapped_column(Text, nullable=False, default="true")
    enabled: Mapped[bool] = mapped_column(default=True)
    cooldown: Mapped[float] = mapped_column(default=0.0)
    
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    def __repr__(self) -> str:
        return f"<TriggerModel(id={self.id}, type={self.type})>"


class ConsequenceModel(Base):
    """Consequence database model."""
    
    __tablename__ = "consequences"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rule_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    trigger_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    params: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    delay: Mapped[float] = mapped_column(default=0.0)
    enabled: Mapped[bool] = mapped_column(default=True)
    
    def __repr__(self) -> str:
        return f"<ConsequenceModel(id={self.id}, action={self.action})>"
