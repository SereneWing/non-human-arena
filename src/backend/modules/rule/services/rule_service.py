"""Rule service implementation."""
from __future__ import annotations

import logging
from typing import List, Optional

from modules.rule.models.rule import RuleModel
from modules.rule.repositories.rule_repository import RuleRepository
from modules.rule.schemas.rule import RuleCreate, RuleResponse, RuleUpdate

logger = logging.getLogger(__name__)


class RuleService:
    """Rule service implementation."""
    
    def __init__(self, repository: RuleRepository):
        self.repository = repository
    
    async def create_rule(self, data: RuleCreate) -> RuleResponse:
        """Create a new rule."""
        rule = await self.repository.create(data)
        return RuleResponse.model_validate(rule)
    
    async def get_rule(self, rule_id: str) -> Optional[RuleResponse]:
        """Get rule by ID."""
        rule = await self.repository.get_by_id(rule_id)
        if not rule:
            return None
        return RuleResponse.model_validate(rule)
    
    async def list_rules(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RuleResponse]:
        """List all rules."""
        rules = await self.repository.list_all(skip=skip, limit=limit)
        return [RuleResponse.model_validate(r) for r in rules]
    
    async def list_rules_by_type(
        self,
        rule_type: str,
    ) -> List[RuleResponse]:
        """List rules by type."""
        rules = await self.repository.list_by_type(rule_type)
        return [RuleResponse.model_validate(r) for r in rules]
    
    async def update_rule(
        self,
        rule_id: str,
        data: RuleUpdate,
    ) -> Optional[RuleResponse]:
        """Update a rule."""
        rule = await self.repository.update(rule_id, data)
        if not rule:
            return None
        return RuleResponse.model_validate(rule)
    
    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule."""
        return await self.repository.delete(rule_id)
    
    async def count_rules(self) -> int:
        """Count total rules."""
        return await self.repository.count()
