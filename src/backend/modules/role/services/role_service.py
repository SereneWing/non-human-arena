"""Role service implementation."""
from __future__ import annotations

import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.event_bus import Event
from core.event_bus import EventType
from events.base import RoleCreatedEvent, RoleDeletedEvent, RoleUpdatedEvent
from modules.role.models.role import RoleModel
from modules.role.repositories.role_repository import RoleRepository
from modules.role.schemas.role import RoleCreate, RoleResponse, RoleUpdate

logger = logging.getLogger(__name__)


class RoleService:
    """Role service implementation."""
    
    def __init__(self, repository: RoleRepository, event_bus: Event = None):
        self.repository = repository
        self.event_bus = event_bus
    
    async def create_role(self, data: RoleCreate) -> RoleResponse:
        """Create a new role."""
        role = await self.repository.create(data)
        response = RoleResponse.model_validate(role)
        
        if self.event_bus:
            await self.event_bus.publish(Event(
                type=EventType.ROLE_CREATED,
                source="role_service",
                data={
                    "role_id": role.id,
                    "name": role.name,
                    "category": role.category,
                },
            ))
        
        logger.info(f"Role created: {role.name} ({role.id})")
        return response
    
    async def get_role(self, role_id: str) -> Optional[RoleResponse]:
        """Get role by ID."""
        role = await self.repository.get_by_id(role_id)
        if not role:
            return None
        return RoleResponse.model_validate(role)
    
    async def get_role_by_name(self, name: str) -> Optional[RoleResponse]:
        """Get role by name."""
        role = await self.repository.get_by_name(name)
        if not role:
            return None
        return RoleResponse.model_validate(role)
    
    async def list_roles(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RoleResponse]:
        """List all roles."""
        roles = await self.repository.list_all(skip=skip, limit=limit)
        return [RoleResponse.model_validate(role) for role in roles]
    
    async def list_roles_by_category(
        self,
        category: str,
    ) -> List[RoleResponse]:
        """List roles by category."""
        roles = await self.repository.list_by_category(category)
        return [RoleResponse.model_validate(role) for role in roles]
    
    async def update_role(
        self,
        role_id: str,
        data: RoleUpdate,
    ) -> Optional[RoleResponse]:
        """Update a role."""
        role = await self.repository.update(role_id, data)
        if not role:
            return None
        
        response = RoleResponse.model_validate(role)
        
        if self.event_bus:
            await self.event_bus.publish(Event(
                type=EventType.ROLE_UPDATED,
                source="role_service",
                data={
                    "role_id": role.id,
                    "name": role.name,
                    "changes": data.model_dump(exclude_unset=True),
                },
            ))
        
        logger.info(f"Role updated: {role.name} ({role.id})")
        return response
    
    async def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        role = await self.repository.get_by_id(role_id)
        if not role:
            return False
        
        role_name = role.name
        success = await self.repository.delete(role_id)
        
        if success and self.event_bus:
            await self.event_bus.publish(Event(
                type=EventType.ROLE_DELETED,
                source="role_service",
                data={
                    "role_id": role_id,
                    "name": role_name,
                },
            ))
        
        if success:
            logger.info(f"Role deleted: {role_name} ({role_id})")
        return success
    
    async def count_roles(self) -> int:
        """Count total roles."""
        return await self.repository.count()
