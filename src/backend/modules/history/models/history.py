"""History SQLAlchemy model."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class HistoryRecord(Base):
    """History record database model."""
    
    __tablename__ = "history"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    # History data as JSON
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, default_factory=dict)
    
    # Format
    format: Mapped[str] = mapped_column(String(50), nullable=False, default="json")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    
    def __repr__(self) -> str:
        return f"<HistoryRecord(id={self.id}, session_id={self.session_id})>"
