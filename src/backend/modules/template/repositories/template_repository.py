"""Template repository implementation."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.template.models.template import TemplateModel, TemplateType
from modules.template.schemas.template import TemplateCreate, TemplateUpdate


class TemplateRepository:
    """SQLAlchemy template repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: TemplateCreate) -> TemplateModel:
        """Create a new template."""
        template = TemplateModel(
            name=data.name,
            type=data.type.value,
            description=data.description,
            category=data.category,
            content=data.content,
            preview=data.preview,
            tags=data.tags,
            metadata=data.metadata,
        )
        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)
        return template
    
    async def get_by_id(self, template_id: str) -> Optional[TemplateModel]:
        """Get template by ID."""
        result = await self.session.execute(
            select(TemplateModel).where(TemplateModel.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[TemplateModel]:
        """List all templates."""
        result = await self.session.execute(
            select(TemplateModel)
            .offset(skip)
            .limit(limit)
            .order_by(TemplateModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def list_by_type(self, template_type: str) -> List[TemplateModel]:
        """List templates by type."""
        result = await self.session.execute(
            select(TemplateModel)
            .where(TemplateModel.type == template_type)
            .order_by(TemplateModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, template_id: str, data: TemplateUpdate) -> Optional[TemplateModel]:
        """Update a template."""
        template = await self.get_by_id(template_id)
        if not template:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        if "type" in update_data and update_data["type"]:
            update_data["type"] = update_data["type"].value
        
        for key, value in update_data.items():
            setattr(template, key, value)
        
        await self.session.flush()
        await self.session.refresh(template)
        return template
    
    async def delete(self, template_id: str) -> bool:
        """Delete a template."""
        template = await self.get_by_id(template_id)
        if not template:
            return False
        
        await self.session.delete(template)
        await self.session.flush()
        return True
    
    async def count(self) -> int:
        """Count total templates."""
        result = await self.session.execute(select(TemplateModel))
        return len(list(result.scalars().all()))
