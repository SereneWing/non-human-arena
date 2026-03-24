# 历史模块仓储层

## 一、历史仓储接口

```python
from typing import Protocol, List, Optional, Dict, Any
from datetime import datetime

class IHistoryRepository(Protocol):
    """历史仓储接口"""
    
    async def save(self, history: SessionHistory) -> str:
        """保存历史"""
        ...
    
    async def get_by_id(self, history_id: str) -> Optional[SessionHistory]:
        """根据ID获取"""
        ...
    
    async def get_by_session_id(self, session_id: str) -> Optional[SessionHistory]:
        """根据会话ID获取"""
        ...
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List[SessionHistory]:
        """列出历史"""
        ...
    
    async def update(self, history: SessionHistory) -> SessionHistory:
        """更新历史"""
        ...
    
    async def delete(self, history_id: str) -> bool:
        """删除历史"""
        ...
    
    async def delete_by_session_id(self, session_id: str) -> bool:
        """根据会话ID删除"""
        ...
    
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SessionHistory]:
        """搜索历史"""
        ...
    
    async def count(self, user_id: Optional[str] = None) -> int:
        """统计数量"""
        ...
```

## 二、SQLAlchemy 仓储实现

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete, func
from typing import List, Optional

class SQLAlchemyHistoryRepository:
    """SQLAlchemy历史仓储"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def save(self, history: SessionHistory) -> str:
        """保存历史"""
        db_history = HistoryModel(
            id=history.id,
            session_id=history.session_id,
            session_name=history.session_name,
            messages=json.dumps([m.to_dict() for m in history.messages]),
            turns=json.dumps([t.to_dict() for t in history.turns]),
            summary=history.summary,
            tags=json.dumps(history.tags),
            metadata=json.dumps(history.metadata),
            created_at=history.created_at,
            updated_at=history.updated_at
        )
        
        self.db.add(db_history)
        await self.db.commit()
        await self.db.refresh(db_history)
        
        return db_history.id
    
    async def get_by_id(self, history_id: str) -> Optional[SessionHistory]:
        """根据ID获取"""
        result = await self.db.execute(
            select(HistoryModel).where(HistoryModel.id == history_id)
        )
        db_history = result.scalar_one_or_none()
        return self._to_entity(db_history) if db_history else None
    
    async def get_by_session_id(self, session_id: str) -> Optional[SessionHistory]:
        """根据会话ID获取"""
        result = await self.db.execute(
            select(HistoryModel).where(HistoryModel.session_id == session_id)
        )
        db_history = result.scalar_one_or_none()
        return self._to_entity(db_history) if db_history else None
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List[SessionHistory]:
        """列出历史"""
        query = select(HistoryModel).order_by(HistoryModel.updated_at.desc())
        
        if user_id:
            query = query.where(HistoryModel.created_by == user_id)
        
        result = await self.db.execute(
            query.offset(skip).limit(limit)
        )
        
        return [self._to_entity(h) for h in result.scalars().all()]
    
    async def update(self, history: SessionHistory) -> SessionHistory:
        """更新历史"""
        result = await self.db.execute(
            select(HistoryModel).where(HistoryModel.id == history.id)
        )
        db_history = result.scalar_one()
        
        db_history.session_name = history.session_name
        db_history.messages = json.dumps([m.to_dict() for m in history.messages])
        db_history.turns = json.dumps([t.to_dict() for t in history.turns])
        db_history.summary = history.summary
        db_history.tags = json.dumps(history.tags)
        db_history.metadata = json.dumps(history.metadata)
        db_history.updated_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(db_history)
        
        return self._to_entity(db_history)
    
    async def delete(self, history_id: str) -> bool:
        """删除历史"""
        result = await self.db.execute(
            sql_delete(HistoryModel).where(HistoryModel.id == history_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_session_id(self, session_id: str) -> bool:
        """根据会话ID删除"""
        result = await self.db.execute(
            sql_delete(HistoryModel).where(HistoryModel.session_id == session_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[SessionHistory]:
        """搜索历史"""
        result = await self.db.execute(
            select(HistoryModel)
            .where(
                or_(
                    HistoryModel.session_name.ilike(f"%{query}%"),
                    HistoryModel.messages.ilike(f"%{query}%")
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(HistoryModel.updated_at.desc())
        )
        
        return [self._to_entity(h) for h in result.scalars().all()]
    
    async def count(self, user_id: Optional[str] = None) -> int:
        """统计数量"""
        query = select(func.count(HistoryModel.id))
        
        if user_id:
            query = query.where(HistoryModel.created_by == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    def _to_entity(self, db_history: HistoryModel) -> SessionHistory:
        """转换为实体"""
        messages = [
            MessageRecord(**m) for m in json.loads(db_history.messages)
        ]
        turns = [
            TurnRecord(**t) for t in json.loads(db_history.turns)
        ]
        
        return SessionHistory(
            id=db_history.id,
            session_id=db_history.session_id,
            session_name=db_history.session_name,
            messages=messages,
            turns=turns,
            summary=db_history.summary,
            tags=json.loads(db_history.tags),
            metadata=json.loads(db_history.metadata),
            created_at=db_history.created_at,
            updated_at=db_history.updated_at
        )
```

## 三、文件存储仓储（可选）

```python
import os
import json
from pathlib import Path

class FileHistoryRepository:
    """文件存储历史仓储"""
    
    def __init__(self, base_path: str = "./data/history"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save(self, history: SessionHistory) -> str:
        """保存历史到文件"""
        file_path = self.base_path / f"{history.session_id}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history.to_dict(), f, ensure_ascii=False, indent=2)
        
        return history.id
    
    async def get_by_session_id(self, session_id: str) -> Optional[SessionHistory]:
        """根据会话ID获取"""
        file_path = self.base_path / f"{session_id}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return SessionHistory.from_dict(data)
    
    async def delete_by_session_id(self, session_id: str) -> bool:
        """根据会话ID删除"""
        file_path = self.base_path / f"{session_id}.json"
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
```
