"""Role repository implementation."""
from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.role.models.role import RoleModel
from modules.role.schemas.role import RoleCreate, RoleUpdate


class IRoleRepository(Protocol):
    """Role repository interface."""
    
    async def create(self, data: RoleCreate) -> RoleModel:
        """Create a new role."""
        ...
    
    async def get_by_id(self, role_id: str) -> Optional[RoleModel]:
        """Get role by ID."""
        ...
    
    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        """Get role by name."""
        ...
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[RoleModel]:
        """List all roles."""
        ...
    
    async def list_by_category(self, category: str) -> List[RoleModel]:
        """List roles by category."""
        ...
    
    async def update(self, role_id: str, data: RoleUpdate) -> Optional[RoleModel]:
        """Update a role."""
        ...
    
    async def delete(self, role_id: str) -> bool:
        """Delete a role."""
        ...
    
    async def exists(self, role_id: str) -> bool:
        """Check if role exists."""
        ...
    
    async def count(self) -> int:
        """Count total roles."""
        ...


class RoleRepository:
    """SQLAlchemy role repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: RoleCreate) -> RoleModel:
        """Create a new role."""
        role = RoleModel(
            name=data.name,
            category=data.category.value,
            description=data.description,
            avatar=data.avatar,
            base_personality=data.base_personality,
            system_prompt=data.system_prompt,
            mental_config=data.mental_config,
            emotional_model=data.emotional_model,
            speaking_style=data.speaking_style,
            skills=data.skills,
            parameters=data.parameters,
            variables=data.variables,
        )
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return role
    
    async def get_by_id(self, role_id: str) -> Optional[RoleModel]:
        """Get role by ID."""
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        """Get role by name."""
        result = await self.session.execute(
            select(RoleModel).where(RoleModel.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[RoleModel]:
        """List all roles."""
        result = await self.session.execute(
            select(RoleModel)
            .offset(skip)
            .limit(limit)
            .order_by(RoleModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def list_by_category(self, category: str) -> List[RoleModel]:
        """List roles by category."""
        result = await self.session.execute(
            select(RoleModel)
            .where(RoleModel.category == category)
            .order_by(RoleModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, role_id: str, data: RoleUpdate) -> Optional[RoleModel]:
        """Update a role."""
        role = await self.get_by_id(role_id)
        if not role:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Handle category enum
        if "category" in update_data and update_data["category"]:
            update_data["category"] = update_data["category"].value
        
        for key, value in update_data.items():
            setattr(role, key, value)
        
        await self.session.flush()
        await self.session.refresh(role)
        return role
    
    async def delete(self, role_id: str) -> bool:
        """Delete a role."""
        role = await self.get_by_id(role_id)
        if not role:
            return False
        
        await self.session.delete(role)
        await self.session.flush()
        return True
    
    async def exists(self, role_id: str) -> bool:
        """Check if role exists."""
        result = await self.session.execute(
            select(RoleModel.id).where(RoleModel.id == role_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def count(self) -> int:
        """Count total roles."""
        result = await self.session.execute(
            select(RoleModel)
        )
        return len(list(result.scalars().all()))
