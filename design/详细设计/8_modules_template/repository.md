# 模板模块仓储层

## 一、模板仓储接口

```python
from typing import Protocol, List, Optional, Dict, Any

class ITemplateRepository(Protocol):
    """模板仓储接口"""
    
    async def create(self, template: Template) -> Template:
        """创建模板"""
        ...
    
    async def get_by_id(self, template_id: str) -> Optional[Template]:
        """根据ID获取模板"""
        ...
    
    async def list_all(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Template]:
        """列出所有模板"""
        ...
    
    async def list_by_type(
        self, 
        template_type: TemplateType,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Template]:
        """按类型列出"""
        ...
    
    async def list_by_category(
        self, 
        category: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Template]:
        """按类别列出"""
        ...
    
    async def update(self, template: Template) -> Template:
        """更新模板"""
        ...
    
    async def delete(self, template_id: str) -> bool:
        """删除模板"""
        ...
    
    async def search(
        self, 
        query: str,
        template_type: Optional[TemplateType] = None
    ) -> List[Template]:
        """搜索模板"""
        ...
    
    async def exists(self, template_id: str) -> bool:
        """检查模板是否存在"""
        ...
    
    async def count(self, template_type: Optional[TemplateType] = None) -> int:
        """统计模板数量"""
        ...
```

## 二、SQLAlchemy 仓储实现

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete, func

class SQLAlchemyTemplateRepository:
    """SQLAlchemy模板仓储"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, template: Template) -> Template:
        """创建模板"""
        db_template = TemplateModel(
            id=template.id,
            name=template.name,
            type=template.type.value,
            content=template.content,
            description=template.description,
            version=template.version,
            variables=json.dumps(template.variables),
            default_values=json.dumps(template.default_values),
            format=template.format.value,
            category=template.category,
            tags=json.dumps(template.tags),
            metadata=json.dumps(template.metadata),
            created_at=template.created_at,
            updated_at=template.updated_at,
            created_by=template.created_by
        )
        
        self.db.add(db_template)
        await self.db.commit()
        await self.db.refresh(db_template)
        
        return self._to_entity(db_template)
    
    async def get_by_id(self, template_id: str) -> Optional[Template]:
        """根据ID获取模板"""
        result = await self.db.execute(
            select(TemplateModel).where(TemplateModel.id == template_id)
        )
        db_template = result.scalar_one_or_none()
        return self._to_entity(db_template) if db_template else None
    
    async def list_all(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Template]:
        """列出所有模板"""
        result = await self.db.execute(
            select(TemplateModel)
            .offset(skip)
            .limit(limit)
            .order_by(TemplateModel.updated_at.desc())
        )
        return [self._to_entity(t) for t in result.scalars().all()]
    
    async def list_by_type(
        self, 
        template_type: TemplateType,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Template]:
        """按类型列出"""
        result = await self.db.execute(
            select(TemplateModel)
            .where(TemplateModel.type == template_type.value)
            .offset(skip)
            .limit(limit)
            .order_by(TemplateModel.updated_at.desc())
        )
        return [self._to_entity(t) for t in result.scalars().all()]
    
    async def update(self, template: Template) -> Template:
        """更新模板"""
        result = await self.db.execute(
            select(TemplateModel).where(TemplateModel.id == template.id)
        )
        db_template = result.scalar_one()
        
        for key, value in template.to_dict().items():
            if hasattr(db_template, key) and key != "id":
                setattr(db_template, key, value)
        
        db_template.updated_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(db_template)
        
        return self._to_entity(db_template)
    
    async def delete(self, template_id: str) -> bool:
        """删除模板"""
        result = await self.db.execute(
            sql_delete(TemplateModel).where(TemplateModel.id == template_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def search(
        self, 
        query: str,
        template_type: Optional[TemplateType] = None
    ) -> List[Template]:
        """搜索模板"""
        stmt = select(TemplateModel).where(
            or_(
                TemplateModel.name.ilike(f"%{query}%"),
                TemplateModel.description.ilike(f"%{query}%"),
                TemplateModel.content.ilike(f"%{query}%")
            )
        )
        
        if template_type:
            stmt = stmt.where(TemplateModel.type == template_type.value)
        
        result = await self.db.execute(stmt)
        return [self._to_entity(t) for t in result.scalars().all()]
    
    def _to_entity(self, db_template: TemplateModel) -> Template:
        """转换为实体"""
        return Template(
            id=db_template.id,
            name=db_template.name,
            type=TemplateType(db_template.type),
            content=db_template.content,
            description=db_template.description,
            version=db_template.version,
            variables=json.loads(db_template.variables),
            default_values=json.loads(db_template.default_values),
            format=TemplateFormat(db_template.format),
            category=db_template.category,
            tags=json.loads(db_template.tags),
            metadata=json.loads(db_template.metadata),
            created_at=db_template.created_at,
            updated_at=db_template.updated_at,
            created_by=db_template.created_by
        )
```
