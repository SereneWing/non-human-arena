"""Roles API router."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from modules.role.repositories.role_repository import RoleRepository
from modules.role.schemas.role import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
)
from modules.role.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["roles"])


def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    """Get role service dependency."""
    repository = RoleRepository(db)
    return RoleService(repository)


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    data: RoleCreate,
    service: RoleService = Depends(get_role_service),
):
    """Create a new role."""
    return await service.create_role(data)


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: RoleService = Depends(get_role_service),
):
    """List all roles."""
    return await service.list_roles(skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    service: RoleService = Depends(get_role_service),
):
    """Get role by ID."""
    role = await service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
):
    """Update role."""
    role = await service.update_role(role_id, data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: str,
    service: RoleService = Depends(get_role_service),
):
    """Delete role."""
    success = await service.delete_role(role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
