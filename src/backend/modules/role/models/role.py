"""Role SQLAlchemy model."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base


class RoleModel(Base):
    """Role database model."""
    
    __tablename__ = "roles"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="debater")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Personality traits stored as JSON
    base_personality: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default_factory=dict,
    )
    
    # System prompt for LLM
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    
    # Configuration stored as JSON
    mental_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    emotional_model: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    speaking_style: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Skills as JSON array
    skills: Mapped[List[str]] = mapped_column(JSON, default_factory=list)
    
    # LLM parameters
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    # Template variables
    variables: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
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
    
    # Relationships
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    participants: Mapped[List["ParticipantModel"]] = relationship(
        "ParticipantModel",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<RoleModel(id={self.id}, name={self.name})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "avatar": self.avatar,
            "base_personality": self.base_personality,
            "system_prompt": self.system_prompt,
            "mental_config": self.mental_config,
            "emotional_model": self.emotional_model,
            "speaking_style": self.speaking_style,
            "skills": self.skills,
            "parameters": self.parameters,
            "variables": self.variables,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Import at bottom to avoid circular imports
from modules.session.models.session import MessageModel, ParticipantModel
