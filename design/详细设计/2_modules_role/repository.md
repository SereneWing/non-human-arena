# 角色模块仓储层

## 一、角色仓储接口

```python
from typing import Protocol, List, Optional, Dict, Any
from abc import ABC, abstractmethod

class IRoleRepository(Protocol):
    """角色仓储接口"""
    
    async def create(self, role: Role) -> Role:
        """创建角色"""
        ...
    
    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """根据ID获取角色"""
        ...
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        ...
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """列出所有角色"""
        ...
    
    async def list_by_category(self, category: RoleCategory) -> List[Role]:
        """按类别列出角色"""
        ...
    
    async def update(self, role: Role) -> Role:
        """更新角色"""
        ...
    
    async def delete(self, role_id: str) -> bool:
        """删除角色"""
        ...
    
    async def exists(self, role_id: str) -> bool:
        """检查角色是否存在"""
        ...
    
    async def search(self, query: str) -> List[Role]:
        """搜索角色"""
        ...
```

## 二、SQLAlchemy 仓储实现

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete
from typing import List, Optional

class SQLAlchemyRoleRepository:
    """SQLAlchemy角色仓储"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, role: Role) -> Role:
        """创建角色"""
        db_role = RoleModel(
            id=role.id,
            name=role.name,
            category=role.category.value,
            description=role.description,
            avatar=role.avatar,
            base_personality=json.dumps(role.base_personality),
            system_prompt=role.system_prompt,
            mental_config=json.dumps(role.mental_config.to_dict()) if role.mental_config else None,
            emotional_model=json.dumps(role.emotional_model.to_dict()) if role.emotional_model else None,
            speaking_style=json.dumps(role.speaking_style.to_dict()) if role.speaking_style else None,
            skills=json.dumps(role.skills),
            parameters=json.dumps(role.parameters),
            variables=json.dumps(role.variables),
            created_at=role.created_at,
            updated_at=role.updated_at
        )
        
        self.db.add(db_role)
        await self.db.commit()
        await self.db.refresh(db_role)
        
        return self._to_entity(db_role)
    
    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """根据ID获取角色"""
        result = await self.db.execute(
            select(RoleModel).where(RoleModel.id == role_id)
        )
        db_role = result.scalar_one_or_none()
        return self._to_entity(db_role) if db_role else None
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """列出所有角色"""
        result = await self.db.execute(
            select(RoleModel)
            .offset(skip)
            .limit(limit)
            .order_by(RoleModel.created_at.desc())
        )
        return [self._to_entity(r) for r in result.scalars().all()]
    
    async def update(self, role: Role) -> Role:
        """更新角色"""
        result = await self.db.execute(
            select(RoleModel).where(RoleModel.id == role.id)
        )
        db_role = result.scalar_one()
        
        for key, value in role.to_dict().items():
            if hasattr(db_role, key) and key != "id":
                setattr(db_role, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_role)
        
        return self._to_entity(db_role)
    
    async def delete(self, role_id: str) -> bool:
        """删除角色"""
        result = await self.db.execute(
            sql_delete(RoleModel).where(RoleModel.id == role_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    def _to_entity(self, db_role: RoleModel) -> Role:
        """转换为实体"""
        return Role(
            id=db_role.id,
            name=db_role.name,
            category=RoleCategory(db_role.category),
            description=db_role.description,
            avatar=db_role.avatar,
            base_personality=json.loads(db_role.base_personality),
            system_prompt=db_role.system_prompt,
            mental_config=MentalConfig.from_dict(json.loads(db_role.mental_config)) if db_role.mental_config else None,
            emotional_model=EmotionalModel.from_dict(json.loads(db_role.emotional_model)) if db_role.emotional_model else None,
            speaking_style=SpeakingStyle.from_dict(json.loads(db_role.speaking_style)) if db_role.speaking_style else None,
            skills=json.loads(db_role.skills),
            parameters=json.loads(db_role.parameters),
            variables=json.loads(db_role.variables),
            created_at=db_role.created_at,
            updated_at=db_role.updated_at
        )
```

## 三、角色模板仓储

```python
class IRoleTemplateRepository(Protocol):
    """角色模板仓储接口"""
    
    async def get_by_id(self, template_id: str) -> Optional[RoleTemplate]:
        """获取模板"""
        ...
    
    async def list_all(self) -> List[RoleTemplate]:
        """列出所有模板"""
        ...
    
    async def list_by_category(self, category: RoleCategory) -> List[RoleTemplate]:
        """按类别列出"""
        ...
    
    async def save(self, template: RoleTemplate) -> RoleTemplate:
        """保存模板"""
        ...
    
    async def delete(self, template_id: str) -> bool:
        """删除模板"""
        ...
```
