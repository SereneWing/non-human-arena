"""AI Decision Engine."""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from llm.base import ChatMessage, MessageRole

logger = logging.getLogger(__name__)


class DecisionType(str, Enum):
    """Decision type enumeration."""
    
    SPEAK = "speak"
    ACT = "act"
    SKIP = "skip"
    WAIT = "wait"


@dataclass
class DecisionContext:
    """Decision context."""
    
    session_id: str
    participant_id: str
    turn_number: int
    recent_messages: List[Dict[str, Any]] = field(default_factory=list)
    session_state: str = "running"
    time_remaining: Optional[float] = None
    rule_states: Dict[str, bool] = field(default_factory=dict)


@dataclass
class AIDecision:
    """AI decision result."""
    
    decision_type: DecisionType
    content: str = ""
    mental_activity: Optional[str] = None
    confidence: float = 1.0
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIDecisionEngine:
    """AI decision engine for determining agent actions."""
    
    def __init__(
        self,
        skip_probability: float = 0.1,
        min_confidence_threshold: float = 0.3,
    ):
        self.skip_probability = skip_probability
        self.min_confidence_threshold = min_confidence_threshold
    
    async def make_decision(
        self,
        context: DecisionContext,
        mental_config: Optional[Dict[str, Any]] = None,
    ) -> AIDecision:
        """Make a decision based on context."""
        mental_config = mental_config or {}
        
        skip_prob = mental_config.get("skip_probability", self.skip_probability)
        
        if random.random() < skip_prob:
            return AIDecision(
                decision_type=DecisionType.SKIP,
                reasoning="Random skip based on configuration",
                confidence=1.0,
            )
        
        return AIDecision(
            decision_type=DecisionType.SPEAK,
            reasoning="Default decision to speak",
            confidence=0.8,
        )
    
    def validate_decision(self, decision: AIDecision) -> bool:
        """Validate a decision."""
        if decision.confidence < self.min_confidence_threshold:
            return False
        
        if decision.decision_type == DecisionType.SPEAK:
            if not decision.content or len(decision.content.strip()) == 0:
                return False
        
        return True
    
    def build_system_prompt(
        self,
        role_name: str,
        role_description: str,
        personality: Dict[str, float],
        speaking_style: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a system prompt from role configuration."""
        personality_str = ", ".join(
            f"{k}: {v}" for k, v in personality.items()
        )
        
        prompt = f"""You are {role_name}.

Role Description:
{role_description}

Personality Traits: {personality_str}
"""
        
        if speaking_style:
            tone = speaking_style.get("tone", "neutral")
            formality = speaking_style.get("formality", 0.5)
            length = speaking_style.get("length_preference", "medium")
            
            prompt += f"""
Speaking Style:
- Tone: {tone}
- Formality: {formality} (0=casual, 1=formal)
- Preferred length: {length}
"""
        
        prompt += """
Please respond in character as the role described above."""
        
        return prompt
