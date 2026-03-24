"""Rules API router."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from modules.rule.repositories.rule_repository import RuleRepository
from modules.rule.schemas.rule import (
    RuleCreate,
    RuleUpdate,
    RuleResponse,
)
from modules.rule.services.rule_service import RuleService

router = APIRouter(prefix="/rules", tags=["rules"])


def get_rule_service(db: AsyncSession = Depends(get_db)) -> RuleService:
    """Get rule service dependency."""
    repository = RuleRepository(db)
    return RuleService(repository)


@router.post("/", response_model=RuleResponse, status_code=201)
async def create_rule(
    data: RuleCreate,
    service: RuleService = Depends(get_rule_service),
):
    """Create a new rule."""
    return await service.create_rule(data)


@router.get("/", response_model=List[RuleResponse])
async def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: RuleService = Depends(get_rule_service),
):
    """List all rules."""
    return await service.list_rules(skip=skip, limit=limit)


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service),
):
    """Get rule by ID."""
    rule = await service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: str,
    data: RuleUpdate,
    service: RuleService = Depends(get_rule_service),
):
    """Update rule."""
    rule = await service.update_rule(rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.delete("/{rule_id}", status_code=204)
async def delete_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service),
):
    """Delete rule."""
    success = await service.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
