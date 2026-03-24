"""Template SQLAlchemy model."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class TemplateType(str, Enum):
    """Template type enumeration."""
    
    ROLE = "role"
    RULE = "rule"
    SCENE = "scene"


class TemplateModel(Base):
    """Template database model."""
    
    __tablename__ = "templates"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default=TemplateType.SCENE.value)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    
    # Template content as JSON
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    # Preview data
    preview: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Tags
    tags: Mapped[list] = mapped_column(JSON, default_factory=list)
    
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
        return f"<TemplateModel(id={self.id}, name={self.name}, type={self.type})>"
