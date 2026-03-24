"""Rule Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class ConstraintBase(BaseModel):
    """Constraint base schema."""
    
    type: ConstraintType
    target: str = "participant"
    condition: str = ""
    error_message: Optional[str] = None
    enabled: bool = True
    priority: int = 0


class ConstraintCreate(ConstraintBase):
    """Constraint creation schema."""
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConstraintResponse(ConstraintBase):
    """Constraint response schema."""
    
    id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class TriggerBase(BaseModel):
    """Trigger base schema."""
    
    type: TriggerType
    event_type: Optional[str] = None
    condition: str = "true"
    enabled: bool = True
    cooldown: float = 0.0


class TriggerCreate(TriggerBase):
    """Trigger creation schema."""
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TriggerResponse(TriggerBase):
    """Trigger response schema."""
    
    id: str
    rule_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class ConsequenceBase(BaseModel):
    """Consequence base schema."""
    
    action: ConsequenceType
    params: Dict[str, Any] = Field(default_factory=dict)
    delay: float = 0.0
    enabled: bool = True


class ConsequenceCreate(ConsequenceBase):
    """Consequence creation schema."""


class ConsequenceResponse(ConsequenceBase):
    """Consequence response schema."""
    
    id: str
    rule_id: str
    trigger_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class RuleBase(BaseModel):
    """Rule base schema."""
    
    name: str = Field(..., min_length=1, max_length=200)
    type: RuleType = Field(default=RuleType.DEBATE)
    description: Optional[str] = None


class RuleCreate(RuleBase):
    """Rule creation schema."""
    
    constraints: List[ConstraintCreate] = Field(default_factory=list)
    triggers: List[TriggerCreate] = Field(default_factory=list)
    consequences: List[ConsequenceCreate] = Field(default_factory=list)
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RuleUpdate(BaseModel):
    """Rule update schema."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[RuleType] = None
    description: Optional[str] = None
    constraints: Optional[List[ConstraintCreate]] = None
    triggers: Optional[List[TriggerCreate]] = None
    consequences: Optional[List[ConsequenceCreate]] = None
    enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class RuleResponse(RuleBase):
    """Rule response schema."""
    
    id: str
    constraints: List[Any] = Field(default_factory=list)
    triggers: List[Any] = Field(default_factory=list)
    consequences: List[Any] = Field(default_factory=list)
    enabled: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
