"""Template Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TemplateType(str, Enum):
    """Template type enumeration."""
    
    ROLE = "role"
    RULE = "rule"
    SCENE = "scene"


class TemplateBase(BaseModel):
    """Template base schema."""
    
    name: str = Field(..., min_length=1, max_length=200)
    type: TemplateType = Field(default=TemplateType.SCENE)
    description: Optional[str] = None
    category: str = Field(default="general")


class TemplateCreate(TemplateBase):
    """Template creation schema."""
    
    content: Dict[str, Any] = Field(default_factory=dict)
    preview: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemplateUpdate(BaseModel):
    """Template update schema."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[TemplateType] = None
    description: Optional[str] = None
    category: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    preview: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TemplateResponse(TemplateBase):
    """Template response schema."""
    
    id: str
    content: Dict[str, Any] = Field(default_factory=dict)
    preview: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
