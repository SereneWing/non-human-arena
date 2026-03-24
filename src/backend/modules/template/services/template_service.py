"""Template service implementation."""
from __future__ import annotations

import logging
from typing import List, Optional

from modules.template.models.template import TemplateModel
from modules.template.repositories.template_repository import TemplateRepository
from modules.template.schemas.template import (
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)

logger = logging.getLogger(__name__)


class TemplateService:
    """Template service implementation."""
    
    def __init__(self, repository: TemplateRepository):
        self.repository = repository
    
    async def create_template(self, data: TemplateCreate) -> TemplateResponse:
        """Create a new template."""
        template = await self.repository.create(data)
        return TemplateResponse.model_validate(template)
    
    async def get_template(self, template_id: str) -> Optional[TemplateResponse]:
        """Get template by ID."""
        template = await self.repository.get_by_id(template_id)
        if not template:
            return None
        return TemplateResponse.model_validate(template)
    
    async def list_templates(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateResponse]:
        """List all templates."""
        templates = await self.repository.list_all(skip=skip, limit=limit)
        return [TemplateResponse.model_validate(t) for t in templates]
    
    async def list_templates_by_type(
        self,
        template_type: str,
    ) -> List[TemplateResponse]:
        """List templates by type."""
        templates = await self.repository.list_by_type(template_type)
        return [TemplateResponse.model_validate(t) for t in templates]
    
    async def update_template(
        self,
        template_id: str,
        data: TemplateUpdate,
    ) -> Optional[TemplateResponse]:
        """Update a template."""
        template = await self.repository.update(template_id, data)
        if not template:
            return None
        return TemplateResponse.model_validate(template)
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        return await self.repository.delete(template_id)
    
    async def count_templates(self) -> int:
        """Count total templates."""
        return await self.repository.count()
