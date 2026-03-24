# 会话模块仓储层

## 一、会话仓储接口

```python
from typing import Protocol, List, Optional, Dict, Any
from datetime import datetime

class ISessionRepository(Protocol):
    """会话仓储接口"""
    
    async def create(self, session: Session) -> Session:
        """创建会话"""
        ...
    
    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """根据ID获取会话"""
        ...
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Session]:
        """列出所有会话"""
        ...
    
    async def list_by_state(self, state: SessionState) -> List[Session]:
        """按状态列出"""
        ...
    
    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Session]:
        """列出用户的会话"""
        ...
    
    async def update(self, session: Session) -> Session:
        """更新会话"""
        ...
    
    async def update_state(self, session_id: str, state: SessionState) -> bool:
        """更新会话状态"""
        ...
    
    async def delete(self, session_id: str) -> bool:
        """删除会话"""
        ...
    
    async def exists(self, session_id: str) -> bool:
        """检查会话是否存在"""
        ...

class IMessageRepository(Protocol):
    """消息仓储接口"""
    
    async def create(self, message: Message) -> Message:
        """创建消息"""
        ...
    
    async def get_by_id(self, message_id: str) -> Optional[Message]:
        """根据ID获取消息"""
        ...
    
    async def get_by_session(
        self, 
        session_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Message]:
        """获取会话的消息"""
        ...
    
    async def get_recent(
        self, 
        session_id: str, 
        limit: int = 20
    ) -> List[Message]:
        """获取最近的消息"""
        ...
    
    async def delete_by_session(self, session_id: str) -> int:
        """删除会话的所有消息"""
        ...

class ITurnRepository(Protocol):
    """回合仓储接口"""
    
    async def create(self, turn: Turn) -> Turn:
        """创建回合"""
        ...
    
    async def get_by_session(self, session_id: str) -> List[Turn]:
        """获取会话的回合"""
        ...
    
    async def get_latest(self, session_id: str) -> Optional[Turn]:
        """获取最新回合"""
        ...
    
    async def count_by_session(self, session_id: str) -> int:
        """统计回合数"""
        ...
```

## 二、SQLAlchemy 仓储实现

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete

class SQLAlchemySessionRepository:
    """SQLAlchemy会话仓储"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create(self, session: Session) -> Session:
        """创建会话"""
        db_session = SessionModel(
            id=session.id,
            name=session.name,
            state=session.state.value,
            template_id=session.template_id,
            role_ids=json.dumps(session.role_ids),
            config=json.dumps(session.config),
            metadata=json.dumps(session.metadata),
            created_at=session.created_at,
            started_at=session.started_at,
            ended_at=session.ended_at,
            created_by=session.created_by,
            participant_ids=json.dumps(session.participant_ids)
        )
        
        self.db.add(db_session)
        await self.db.commit()
        await self.db.refresh(db_session)
        
        return self._to_entity(db_session)
    
    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """根据ID获取会话"""
        result = await self.db.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        db_session = result.scalar_one_or_none()
        return self._to_entity(db_session) if db_session else None
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Session]:
        """列出所有会话"""
        result = await self.db.execute(
            select(SessionModel)
            .offset(skip)
            .limit(limit)
            .order_by(SessionModel.created_at.desc())
        )
        return [self._to_entity(s) for s in result.scalars().all()]
    
    async def update_state(self, session_id: str, state: SessionState) -> bool:
        """更新会话状态"""
        result = await self.db.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        db_session = result.scalar_one_or_none()
        
        if db_session:
            db_session.state = state.value
            if state == SessionState.RUNNING and not db_session.started_at:
                db_session.started_at = datetime.now()
            elif state in [SessionState.COMPLETED, SessionState.CANCELLED]:
                db_session.ended_at = datetime.now()
            
            await self.db.commit()
            return True
        return False
    
    async def delete(self, session_id: str) -> bool:
        """删除会话"""
        result = await self.db.execute(
            sql_delete(SessionModel).where(SessionModel.id == session_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    def _to_entity(self, db_session: SessionModel) -> Session:
        """转换为实体"""
        return Session(
            id=db_session.id,
            name=db_session.name,
            state=SessionState(db_session.state),
            template_id=db_session.template_id,
            role_ids=json.loads(db_session.role_ids),
            config=json.loads(db_session.config),
            metadata=json.loads(db_session.metadata),
            created_at=db_session.created_at,
            started_at=db_session.started_at,
            ended_at=db_session.ended_at,
            created_by=db_session.created_by,
            participant_ids=json.loads(db_session.participant_ids)
        )
```
