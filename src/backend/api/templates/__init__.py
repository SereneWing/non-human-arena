"""Templates API router."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/roles")
async def list_role_templates():
    """List role templates."""
    return {
        "templates": [
            {
                "id": "debater",
                "name": "辩手",
                "description": "标准辩论角色模板",
            },
            {
                "id": "mediator",
                "name": "主持人",
                "description": "讨论主持人角色模板",
            },
        ]
    }


@router.get("/rules")
async def list_rule_templates():
    """List rule templates."""
    return {
        "templates": [
            {
                "id": "free_debate",
                "name": "自由辩论",
                "description": "无限制自由辩论规则",
            },
            {
                "id": "formal_debate",
                "name": "正式辩论",
                "description": "有顺序和时间限制的正式辩论",
            },
        ]
    }


@router.get("/scenes")
async def list_scene_templates():
    """List scene templates."""
    return {
        "templates": [
            {
                "id": "academic_debate",
                "name": "学术辩论",
                "description": "学术话题的正式辩论场景",
            },
            {
                "id": "business_negotiation",
                "name": "商业谈判",
                "description": "模拟商业谈判场景",
            },
        ]
    }
