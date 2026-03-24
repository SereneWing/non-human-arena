"""Role Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoleCategory(str, Enum):
    """Role category enumeration."""
    
    DEBATER = "debater"
    MEDIATOR = "mediator"
    NARRATOR = "narrator"
    JUDGE = "judge"
    PLAYER = "player"
    TEACHER = "teacher"
    STUDENT = "student"
    CUSTOM = "custom"


class RoleBase(BaseModel):
    """Role base schema."""
    
    name: str = Field(..., min_length=1, max_length=100)
    category: RoleCategory = Field(default=RoleCategory.DEBATER)
    description: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = Field(None, max_length=500)


class RoleCreate(RoleBase):
    """Role creation schema."""
    
    base_personality: Dict[str, float] = Field(default_factory=dict)
    system_prompt: str = Field(default="")
    mental_config: Optional[Dict[str, Any]] = Field(None)
    emotional_model: Optional[Dict[str, Any]] = Field(None)
    speaking_style: Optional[Dict[str, Any]] = Field(None)
    skills: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)


class RoleUpdate(BaseModel):
    """Role update schema."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[RoleCategory] = None
    description: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = Field(None, max_length=500)
    base_personality: Optional[Dict[str, float]] = None
    system_prompt: Optional[str] = None
    mental_config: Optional[Dict[str, Any]] = None
    emotional_model: Optional[Dict[str, Any]] = None
    speaking_style: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None


class RoleResponse(RoleBase):
    """Role response schema."""
    
    id: str
    base_personality: Dict[str, float] = Field(default_factory=dict)
    system_prompt: str = ""
    mental_config: Optional[Dict[str, Any]] = None
    emotional_model: Optional[Dict[str, Any]] = None
    speaking_style: Optional[Dict[str, Any]] = None
    skills: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RoleListResponse(BaseModel):
    """Role list response schema."""
    
    items: List[RoleResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
