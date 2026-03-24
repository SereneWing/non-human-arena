"""History Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Export format enumeration."""
    
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


class HistoryExportRequest(BaseModel):
    """History export request schema."""
    
    session_id: str
    format: ExportFormat = Field(default=ExportFormat.JSON)
    include_metadata: bool = Field(default=True)


class HistoryExportResponse(BaseModel):
    """History export response schema."""
    
    session_id: str
    format: ExportFormat
    content: str
    created_at: datetime
    file_url: Optional[str] = None
