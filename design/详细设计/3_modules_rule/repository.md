# 规则模块仓储层

## 一、规则仓储接口

```python
from typing import Protocol, List, Optional, Dict, Any
from abc import ABC, abstractmethod

class IRuleRepository(Protocol):
    """规则仓储接口"""
    
    async def create(self, rule: Rule) -> Rule:
        """创建规则"""
        ...
    
    async def get_by_id(self, rule_id: str) -> Optional[Rule]:
        """根据ID获取规则"""
        ...
    
    async def get_by_session(self, session_id: str) -> List[Rule]:
        """获取会话的所有规则"""
        ...
    
    async def update(self, rule: Rule) -> Rule:
        """更新规则"""
        ...
    
    async def delete(self, rule_id: str) -> bool:
        """删除规则"""
        ...
    
    async def delete_by_session(self, session_id: str) -> int:
        """删除会话的所有规则"""
        ...
    
    async def enable(self, rule_id: str) -> bool:
        """启用规则"""
        ...
    
    async def disable(self, rule_id: str) -> bool:
        """禁用规则"""
        ...

class IRuleTemplateRepository(Protocol):
    """规则模板仓储接口"""
    
    async def get_by_id(self, template_id: str) -> Optional[RuleTemplate]:
        """获取模板"""
        ...
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[RuleTemplate]:
        """列出所有模板"""
        ...
    
    async def list_by_type(self, rule_type: RuleType) -> List[RuleTemplate]:
        """按类型列出"""
        ...
    
    async def save(self, template: RuleTemplate) -> RuleTemplate:
        """保存模板"""
        ...
    
    async def delete(self, template_id: str) -> bool:
        """删除模板"""
        ...
    
    async def search(self, query: str) -> List[RuleTemplate]:
        """搜索模板"""
        ...
```

## 二、SQLAlchemy 仓储实现

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete, update as sql_update

class SQLAlchemyRuleRepository:
    """SQLAlchemy规则仓储"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, rule: Rule) -> Rule:
        """创建规则"""
        db_rule = RuleModel(
            id=rule.id,
            template_id=rule.template_id,
            session_id=rule.session_id,
            name=rule.name,
            constraints=json.dumps([c.to_dict() for c in rule.constraints]),
            triggers=json.dumps([t.to_dict() for t in rule.triggers]),
            enabled=rule.enabled,
            created_at=rule.created_at
        )
        
        self.db.add(db_rule)
        await self.db.commit()
        await self.db.refresh(db_rule)
        
        return self._to_entity(db_rule)
    
    async def get_by_id(self, rule_id: str) -> Optional[Rule]:
        """根据ID获取规则"""
        result = await self.db.execute(
            select(RuleModel).where(RuleModel.id == rule_id)
        )
        db_rule = result.scalar_one_or_none()
        return self._to_entity(db_rule) if db_rule else None
    
    async def get_by_session(self, session_id: str) -> List[Rule]:
        """获取会话的所有规则"""
        result = await self.db.execute(
            select(RuleModel).where(RuleModel.session_id == session_id)
        )
        return [self._to_entity(r) for r in result.scalars().all()]
    
    async def delete(self, rule_id: str) -> bool:
        """删除规则"""
        result = await self.db.execute(
            sql_delete(RuleModel).where(RuleModel.id == rule_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def enable(self, rule_id: str) -> bool:
        """启用规则"""
        result = await self.db.execute(
            sql_update(RuleModel)
            .where(RuleModel.id == rule_id)
            .values(enabled=True)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def disable(self, rule_id: str) -> bool:
        """禁用规则"""
        result = await self.db.execute(
            sql_update(RuleModel)
            .where(RuleModel.id == rule_id)
            .values(enabled=False)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    def _to_entity(self, db_rule: RuleModel) -> Rule:
        """转换为实体"""
        constraints = [
            Constraint.from_dict(c) 
            for c in json.loads(db_rule.constraints)
        ]
        triggers = [
            Trigger.from_dict(t) 
            for t in json.loads(db_rule.triggers)
        ]
        
        return Rule(
            id=db_rule.id,
            template_id=db_rule.template_id,
            session_id=db_rule.session_id,
            name=db_rule.name,
            constraints=constraints,
            triggers=triggers,
            enabled=db_rule.enabled,
            created_at=db_rule.created_at
        )
```
