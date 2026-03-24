"""Rule engine implementation."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.event_bus import Event
from modules.rule.models.rule import (
    ConstraintType,
    RuleModel,
)

logger = logging.getLogger(__name__)


@dataclass
class ConstraintResult:
    """Constraint evaluation result."""
    
    satisfied: bool
    violation: Optional[Dict[str, Any]] = None
    constraint_id: Optional[str] = None


@dataclass
class RuleCheckResult:
    """Rule check result."""
    
    session_id: str
    satisfied: List[Dict[str, Any]] = field(default_factory=list)
    violated: List[Dict[str, Any]] = field(default_factory=list)
    triggered: List[Dict[str, Any]] = field(default_factory=list)


class RuleEngine:
    """Rule engine for evaluating and executing rules."""
    
    def __init__(self, event_bus: Event = None):
        self.event_bus = event_bus
    
    async def evaluate_constraints(
        self,
        constraints: List[Dict[str, Any]],
        message: str,
        context: Dict[str, Any],
    ) -> List[ConstraintResult]:
        """Evaluate constraints against a message."""
        results = []
        
        for constraint in constraints:
            if not constraint.get("enabled", True):
                continue
            
            result = await self._evaluate_constraint(constraint, message, context)
            results.append(result)
        
        return results
    
    async def _evaluate_constraint(
        self,
        constraint: Dict[str, Any],
        message: str,
        context: Dict[str, Any],
    ) -> ConstraintResult:
        """Evaluate a single constraint."""
        constraint_type = constraint.get("type")
        
        if constraint_type == ConstraintType.MESSAGE_LENGTH.value:
            min_length = constraint.get("params", {}).get("min_length", 0)
            max_length = constraint.get("params", {}).get("max_length", float("inf"))
            
            if not min_length <= len(message) <= max_length:
                return ConstraintResult(
                    satisfied=False,
                    violation={
                        "type": constraint_type,
                        "message": f"Message length must be between {min_length} and {max_length}",
                    },
                    constraint_id=constraint.get("id"),
                )
        
        elif constraint_type == ConstraintType.WORD_COUNT.value:
            min_words = constraint.get("params", {}).get("min_words", 0)
            max_words = constraint.get("params", {}).get("max_words", float("inf"))
            
            word_count = len(message.split())
            if not min_words <= word_count <= max_words:
                return ConstraintResult(
                    satisfied=False,
                    violation={
                        "type": constraint_type,
                        "message": f"Word count must be between {min_words} and {max_words}",
                    },
                    constraint_id=constraint.get("id"),
                )
        
        elif constraint_type == ConstraintType.KEYWORD_REQUIRED.value:
            keywords = constraint.get("params", {}).get("keywords", [])
            
            missing = [kw for kw in keywords if kw not in message]
            if missing:
                return ConstraintResult(
                    satisfied=False,
                    violation={
                        "type": constraint_type,
                        "message": f"Message must contain keywords: {', '.join(missing)}",
                    },
                    constraint_id=constraint.get("id"),
                )
        
        elif constraint_type == ConstraintType.KEYWORD_FORBIDDEN.value:
            forbidden = constraint.get("params", {}).get("keywords", [])
            
            found = [kw for kw in forbidden if kw in message]
            if found:
                return ConstraintResult(
                    satisfied=False,
                    violation={
                        "type": constraint_type,
                        "message": f"Message contains forbidden keywords: {', '.join(found)}",
                    },
                    constraint_id=constraint.get("id"),
                )
        
        return ConstraintResult(satisfied=True, constraint_id=constraint.get("id"))
    
    async def check_rules(
        self,
        rules: List[RuleModel],
        session_id: str,
        message: str,
        context: Dict[str, Any],
    ) -> RuleCheckResult:
        """Check all rules for a session."""
        result = RuleCheckResult(session_id=session_id)
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            constraints = rule.constraints or []
            constraint_results = await self.evaluate_constraints(
                constraints, message, context
            )
            
            satisfied = [r for r in constraint_results if r.satisfied]
            violated = [r for r in constraint_results if not r.satisfied]
            
            if violated:
                result.violated.append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "violations": [
                        v.violation for v in violated if v.violation
                    ],
                })
            else:
                result.satisfied.append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                })
        
        return result
    
    async def execute_consequence(
        self,
        consequence: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        """Execute a consequence action."""
        action = consequence.get("action")
        params = consequence.get("params", {})
        
        try:
            if action == "send_message":
                content = params.get("content", "")
                logger.info(f"Execute consequence: send_message - {content}")
                return True
            
            elif action == "skip_turn":
                participant_id = params.get("participant_id")
                logger.info(f"Execute consequence: skip_turn for {participant_id}")
                return True
            
            elif action == "end_session":
                reason = params.get("reason", "Rule triggered")
                logger.info(f"Execute consequence: end_session - {reason}")
                return True
            
            else:
                logger.warning(f"Unknown consequence action: {action}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to execute consequence: {e}")
            return False
