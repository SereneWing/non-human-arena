"""Rule repository implementation."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.rule.models.rule import RuleModel
from modules.rule.schemas.rule import RuleCreate, RuleUpdate


class RuleRepository:
    """SQLAlchemy rule repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: RuleCreate) -> RuleModel:
        """Create a new rule."""
        constraints = [
            {
                **c.model_dump(),
                "id": str(i),
            }
            for i, c in enumerate(data.constraints)
        ]
        
        triggers = [
            {
                **t.model_dump(exclude={"metadata"}),
                "id": str(i),
            }
            for i, t in enumerate(data.triggers)
        ]
        
        consequences = [c.model_dump() for c in data.consequences]
        
        rule = RuleModel(
            name=data.name,
            type=data.type.value,
            description=data.description,
            constraints=constraints,
            triggers=triggers,
            consequences=consequences,
            enabled=data.enabled,
            metadata=data.metadata,
        )
        
        self.session.add(rule)
        await self.session.flush()
        await self.session.refresh(rule)
        return rule
    
    async def get_by_id(self, rule_id: str) -> Optional[RuleModel]:
        """Get rule by ID."""
        result = await self.session.execute(
            select(RuleModel).where(RuleModel.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[RuleModel]:
        """List all rules."""
        result = await self.session.execute(
            select(RuleModel)
            .offset(skip)
            .limit(limit)
            .order_by(RuleModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def list_by_type(self, rule_type: str) -> List[RuleModel]:
        """List rules by type."""
        result = await self.session.execute(
            select(RuleModel)
            .where(RuleModel.type == rule_type)
            .order_by(RuleModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, rule_id: str, data: RuleUpdate) -> Optional[RuleModel]:
        """Update a rule."""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        if "type" in update_data and update_data["type"]:
            update_data["type"] = update_data["type"].value
        
        if "constraints" in update_data and update_data["constraints"]:
            update_data["constraints"] = [
                c.model_dump() if hasattr(c, "model_dump") else c
                for c in update_data["constraints"]
            ]
        
        if "triggers" in update_data and update_data["triggers"]:
            update_data["triggers"] = [
                t.model_dump() if hasattr(t, "model_dump") else t
                for t in update_data["triggers"]
            ]
        
        if "consequences" in update_data and update_data["consequences"]:
            update_data["consequences"] = [
                c.model_dump() if hasattr(c, "model_dump") else c
                for c in update_data["consequences"]
            ]
        
        for key, value in update_data.items():
            setattr(rule, key, value)
        
        await self.session.flush()
        await self.session.refresh(rule)
        return rule
    
    async def delete(self, rule_id: str) -> bool:
        """Delete a rule."""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return False
        
        await self.session.delete(rule)
        await self.session.flush()
        return True
    
    async def count(self) -> int:
        """Count total rules."""
        result = await self.session.execute(select(RuleModel))
        return len(list(result.scalars().all()))
