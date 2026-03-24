"""Session repository implementation."""
from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.session.models.session import (
    MessageModel,
    ParticipantModel,
    SessionModel,
    SessionState,
)
from modules.session.schemas.session import (
    MessageCreate,
    ParticipantCreate,
    SessionCreate,
    SessionUpdate,
)


class ISessionRepository(Protocol):
    """Session repository interface."""
    
    async def create(self, data: SessionCreate) -> SessionModel:
        """Create a new session."""
        ...
    
    async def get_by_id(self, session_id: str) -> Optional[SessionModel]:
        """Get session by ID."""
        ...
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[SessionModel]:
        """List all sessions."""
        ...
    
    async def list_by_state(self, state: SessionState) -> List[SessionModel]:
        """List sessions by state."""
        ...
    
    async def update(self, session_id: str, data: SessionUpdate) -> Optional[SessionModel]:
        """Update a session."""
        ...
    
    async def delete(self, session_id: str) -> bool:
        """Delete a session."""
        ...
    
    async def update_state(self, session_id: str, state: SessionState) -> Optional[SessionModel]:
        """Update session state."""
        ...
    
    async def count(self) -> int:
        """Count total sessions."""
        ...


class SessionRepository:
    """SQLAlchemy session repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: SessionCreate) -> SessionModel:
        """Create a new session."""
        session = SessionModel(
            name=data.name,
            topic=data.topic,
            template_id=data.template_id,
            role_ids=data.role_ids,
            config=data.config,
            metadata=data.metadata,
            state=SessionState.CREATED.value,
        )
        self.session.add(session)
        await self.session.flush()
        await self.session.refresh(session)
        return session
    
    async def get_by_id(self, session_id: str) -> Optional[SessionModel]:
        """Get session by ID."""
        result = await self.session.execute(
            select(SessionModel)
            .where(SessionModel.id == session_id)
            .options(
                selectinload(SessionModel.participants),
                selectinload(SessionModel.messages),
            )
        )
        return result.scalar_one_or_none()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[SessionModel]:
        """List all sessions."""
        result = await self.session.execute(
            select(SessionModel)
            .offset(skip)
            .limit(limit)
            .order_by(SessionModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def list_by_state(self, state: SessionState) -> List[SessionModel]:
        """List sessions by state."""
        result = await self.session.execute(
            select(SessionModel)
            .where(SessionModel.state == state.value)
            .order_by(SessionModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, session_id: str, data: SessionUpdate) -> Optional[SessionModel]:
        """Update a session."""
        session = await self.get_by_id(session_id)
        if not session:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Handle state enum
        if "state" in update_data and update_data["state"]:
            update_data["state"] = update_data["state"].value
        
        for key, value in update_data.items():
            setattr(session, key, value)
        
        await self.session.flush()
        await self.session.refresh(session)
        return session
    
    async def delete(self, session_id: str) -> bool:
        """Delete a session."""
        session = await self.get_by_id(session_id)
        if not session:
            return False
        
        await self.session.delete(session)
        await self.session.flush()
        return True
    
    async def update_state(self, session_id: str, state: SessionState) -> Optional[SessionModel]:
        """Update session state."""
        session = await self.get_by_id(session_id)
        if not session:
            return None
        
        session.state = state.value
        
        # Set timestamps based on state
        from datetime import datetime
        if state == SessionState.RUNNING and not session.started_at:
            session.started_at = datetime.now()
        elif state in [SessionState.COMPLETED, SessionState.CANCELLED]:
            session.ended_at = datetime.now()
        
        await self.session.flush()
        await self.session.refresh(session)
        return session
    
    async def count(self) -> int:
        """Count total sessions."""
        result = await self.session.execute(
            select(func.count(SessionModel.id))
        )
        return result.scalar_one()


class MessageRepository:
    """Message repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, session_id: str, data: MessageCreate) -> MessageModel:
        """Create a new message."""
        # Get next turn number
        result = await self.session.execute(
            select(func.max(MessageModel.turn_number))
            .where(MessageModel.session_id == session_id)
        )
        max_turn = result.scalar_one() or 0
        
        message = MessageModel(
            session_id=session_id,
            participant_id=data.participant_id,
            role_id=data.role_id,
            type=data.type,
            content=data.content,
            mental_activity=data.mental_activity,
            turn_number=max_turn + 1,
            metadata=data.metadata,
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message
    
    async def get_by_id(self, message_id: str) -> Optional[MessageModel]:
        """Get message by ID."""
        result = await self.session.execute(
            select(MessageModel).where(MessageModel.id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[MessageModel]:
        """List messages by session."""
        result = await self.session.execute(
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .offset(skip)
            .limit(limit)
            .order_by(MessageModel.created_at)
        )
        return list(result.scalars().all())
    
    async def count_by_session(self, session_id: str) -> int:
        """Count messages in a session."""
        result = await self.session.execute(
            select(func.count(MessageModel.id))
            .where(MessageModel.session_id == session_id)
        )
        return result.scalar_one()


class ParticipantRepository:
    """Participant repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, session_id: str, data: ParticipantCreate) -> ParticipantModel:
        """Create a new participant."""
        participant = ParticipantModel(
            session_id=session_id,
            role_id=data.role_id,
            name=data.name,
            is_ai=data.is_ai,
            metadata=data.metadata,
        )
        self.session.add(participant)
        await self.session.flush()
        await self.session.refresh(participant)
        return participant
    
    async def get_by_id(self, participant_id: str) -> Optional[ParticipantModel]:
        """Get participant by ID."""
        result = await self.session.execute(
            select(ParticipantModel).where(ParticipantModel.id == participant_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_session(self, session_id: str) -> List[ParticipantModel]:
        """List participants by session."""
        result = await self.session.execute(
            select(ParticipantModel)
            .where(ParticipantModel.session_id == session_id)
            .order_by(ParticipantModel.joined_at)
        )
        return list(result.scalars().all())
    
    async def update_status(
        self,
        participant_id: str,
        is_active: bool,
    ) -> Optional[ParticipantModel]:
        """Update participant active status."""
        from datetime import datetime
        participant = await self.get_by_id(participant_id)
        if not participant:
            return None
        
        participant.is_active = is_active
        if not is_active:
            participant.left_at = datetime.now()
        
        await self.session.flush()
        await self.session.refresh(participant)
        return participant
