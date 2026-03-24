# 规则模块 API 路由

## 一、规则 API

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/rules", tags=["规则"])

# ==================== 规则管理 ====================

@router.get("/", response_model=List[RuleResponse])
async def list_rules(
    skip: int = 0,
    limit: int = 100,
    rule_type: Optional[str] = None,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """列出规则"""
    if session_id:
        rules = await rule_service.get_rules_by_session(session_id)
    else:
        rules = await rule_service.list_templates(
            skip=skip,
            limit=limit,
            rule_type=rule_type
        )
    return rules

@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """获取规则详情"""
    rule = await rule_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    return rule

@router.post("/", response_model=RuleResponse)
async def create_rule(
    data: CreateRuleRequest,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """创建规则"""
    try:
        rule = await rule_service.create_rule(data, current_user.id)
        return rule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: str,
    data: UpdateRuleRequest,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """更新规则"""
    rule = await rule_service.update_rule(rule_id, data)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    return rule

@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """删除规则"""
    success = await rule_service.delete_rule(rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则不存在"
        )
    return {"success": True}

# ==================== 规则模板管理 ====================

@router.get("/templates/", response_model=List[RuleTemplateResponse])
async def list_rule_templates(
    skip: int = 0,
    limit: int = 100,
    rule_type: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """列出规则模板"""
    templates = await rule_service.list_templates(
        skip=skip,
        limit=limit,
        rule_type=rule_type,
        category=category
    )
    return templates

@router.get("/templates/{template_id}", response_model=RuleTemplateResponse)
async def get_rule_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """获取规则模板详情"""
    template = await rule_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则模板不存在"
        )
    return template

@router.post("/templates/", response_model=RuleTemplateResponse)
async def create_rule_template(
    data: CreateRuleTemplateRequest,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """创建规则模板"""
    try:
        template = await rule_service.create_template(data, current_user.id)
        return template
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/templates/{template_id}", response_model=RuleTemplateResponse)
async def update_rule_template(
    template_id: str,
    data: UpdateRuleTemplateRequest,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """更新规则模板"""
    template = await rule_service.update_template(template_id, data)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则模板不存在"
        )
    return template

@router.delete("/templates/{template_id}")
async def delete_rule_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    rule_service: RuleService = Depends(get_rule_service)
):
    """删除规则模板"""
    success = await rule_service.delete_template(template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="规则模板不存在"
        )
    return {"success": True}

# ==================== 规则检查 ====================

@router.post("/check", response_model=RuleCheckResponse)
async def check_rules(
    session_id: str,
    message: str,
    participant_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    rule_engine: RuleEngine = Depends(get_rule_engine)
):
    """检查消息是否违反规则"""
    result = await rule_engine.check_message(
        session_id=session_id,
        message=message,
        participant_id=participant_id
    )
    return result

@router.post("/validate")
async def validate_constraint(
    constraint_type: str,
    value: str,
    target: str,
    current_user: User = Depends(get_current_user),
    rule_engine: RuleEngine = Depends(get_rule_engine)
):
    """验证约束条件"""
    try:
        result = await rule_engine.validate_constraint(
            constraint_type=constraint_type,
            value=value,
            target=target
        )
        return {"valid": result}
    except ValueError as e:
        return {"valid": False, "error": str(e)}

# ==================== 请求/响应模型 ====================

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ConstraintSchema(BaseModel):
    id: str
    type: str
    target: str = "participant"
    condition: str = ""
    error_message: str = ""
    enabled: bool = True
    priority: int = 0

class TriggerSchema(BaseModel):
    id: str
    type: str
    event_type: Optional[str] = None
    condition: str = "true"
    consequence: Dict[str, Any]
    enabled: bool = True
    cooldown: float = 0

class CreateRuleRequest(BaseModel):
    name: str
    template_id: Optional[str] = None
    session_id: str
    constraints: List[ConstraintSchema] = Field(default_factory=list)
    triggers: List[TriggerSchema] = Field(default_factory=list)

class UpdateRuleRequest(BaseModel):
    name: Optional[str] = None
    constraints: Optional[List[ConstraintSchema]] = None
    triggers: Optional[List[TriggerSchema]] = None
    enabled: Optional[bool] = None

class CreateRuleTemplateRequest(BaseModel):
    name: str
    type: str
    description: str = ""
    category: str = "general"
    constraints: List[ConstraintSchema] = Field(default_factory=list)
    triggers: List[TriggerSchema] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UpdateRuleTemplateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    constraints: Optional[List[ConstraintSchema]] = None
    triggers: Optional[List[TriggerSchema]] = None
    metadata: Optional[Dict[str, Any]] = None

class RuleResponse(BaseModel):
    id: str
    name: str
    template_id: str
    session_id: str
    constraints: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RuleTemplateResponse(BaseModel):
    id: str
    name: str
    type: str
    description: str
    category: str
    constraints: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RuleCheckResponse(BaseModel):
    session_id: str
    satisfied: bool
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    triggered_rules: List[str] = Field(default_factory=list)
    timestamp: datetime
```
