"""Session service implementation."""
from __future__ import annotations

import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.event_bus import Event, EventType
from events.base import (
    SessionCreatedEvent,
    SessionEndedEvent,
    SessionErrorEvent,
    SessionStartedEvent,
)
from modules.session.models.session import SessionState
from modules.session.repositories.session_repository import (
    MessageRepository,
    ParticipantRepository,
    SessionRepository,
)
from modules.session.schemas.session import (
    MessageCreate,
    MessageResponse,
    ParticipantCreate,
    ParticipantResponse,
    SessionCreate,
    SessionDetailResponse,
    SessionListResponse,
    SessionResponse,
    SessionUpdate,
)
from modules.session.services.state_machine import SessionStateMachine

logger = logging.getLogger(__name__)


class SessionService:
    """Session service implementation."""
    
    def __init__(
        self,
        session_repository: SessionRepository,
        message_repository: MessageRepository,
        participant_repository: ParticipantRepository,
        state_machine: SessionStateMachine,
        event_bus: Event = None,
    ):
        self.session_repository = session_repository
        self.message_repository = message_repository
        self.participant_repository = participant_repository
        self.state_machine = state_machine
        self.event_bus = event_bus
    
    async def create_session(self, data: SessionCreate) -> SessionResponse:
        """Create a new session."""
        session = await self.session_repository.create(data)
        
        # Create participants for each role
        # Note: In a real implementation, we would get role names from role IDs
        for role_id in data.role_ids:
            participant_data = ParticipantCreate(
                role_id=role_id,
                name=f"Participant {role_id[:8]}",
                is_ai=True,
            )
            await self.participant_repository.create(session.id, participant_data)
        
        response = SessionResponse.model_validate(session)
        
        if self.event_bus:
            await self.event_bus.publish(Event(
                type=EventType.SESSION_CREATED,
                source="session_service",
                session_id=session.id,
                data={
                    "session_id": session.id,
                    "name": session.name,
                    "topic": session.topic,
                    "participant_ids": [p.id for p in session.participants],
                },
            ))
        
        logger.info(f"Session created: {session.name} ({session.id})")
        return response
    
    async def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Get session by ID."""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return None
        return SessionResponse.model_validate(session)
    
    async def get_session_detail(self, session_id: str) -> Optional[SessionDetailResponse]:
        """Get session detail with participants."""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return None
        
        participants = await self.participant_repository.list_by_session(session_id)
        message_count = await self.message_repository.count_by_session(session_id)
        
        return SessionDetailResponse(
            **SessionResponse.model_validate(session).model_dump(),
            participants=[ParticipantResponse.model_validate(p) for p in participants],
            message_count=message_count,
        )
    
    async def list_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> SessionListResponse:
        """List all sessions."""
        sessions = await self.session_repository.list_all(skip=skip, limit=limit)
        total = await self.session_repository.count()
        
        return SessionListResponse(
            items=[SessionResponse.model_validate(s) for s in sessions],
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            has_more=skip + limit < total,
        )
    
    async def update_session(
        self,
        session_id: str,
        data: SessionUpdate,
    ) -> Optional[SessionResponse]:
        """Update a session."""
        session = await self.session_repository.update(session_id, data)
        if not session:
            return None
        return SessionResponse.model_validate(session)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        return await self.session_repository.delete(session_id)
    
    async def start_session(self, session_id: str) -> Optional[SessionResponse]:
        """Start a session."""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return None
        
        current_state = SessionState(session.state)
        target_state = SessionState.RUNNING
        
        if not self.state_machine.can_transition(current_state, target_state):
            logger.warning(
                f"Cannot transition from {current_state} to {target_state}"
            )
            return None
        
        session = await self.session_repository.update_state(
            session_id,
            target_state,
        )
        
        if self.event_bus:
            participants = await self.participant_repository.list_by_session(session_id)
            await self.event_bus.publish(Event(
                type=EventType.SESSION_STARTED,
                source="session_service",
                session_id=session_id,
                data={
                    "session_id": session_id,
                    "topic": session.topic,
                    "participant_ids": [p.id for p in participants],
                },
            ))
        
        logger.info(f"Session started: {session_id}")
        return SessionResponse.model_validate(session)
    
    async def pause_session(self, session_id: str) -> Optional[SessionResponse]:
        """Pause a session."""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return None
        
        current_state = SessionState(session.state)
        target_state = SessionState.PAUSED
        
        if not self.state_machine.can_transition(current_state, target_state):
            return None
        
        session = await self.session_repository.update_state(
            session_id,
            target_state,
        )
        
        logger.info(f"Session paused: {session_id}")
        return SessionResponse.model_validate(session)
    
    async def resume_session(self, session_id: str) -> Optional[SessionResponse]:
        """Resume a session."""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return None
        
        current_state = SessionState(session.state)
        target_state = SessionState.RUNNING
        
        if not self.state_machine.can_transition(current_state, target_state):
            return None
        
        session = await self.session_repository.update_state(
            session_id,
            target_state,
        )
        
        logger.info(f"Session resumed: {session_id}")
        return SessionResponse.model_validate(session)
    
    async def end_session(
        self,
        session_id: str,
        reason: str = None,
    ) -> Optional[SessionResponse]:
        """End a session."""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return None
        
        current_state = SessionState(session.state)
        target_state = SessionState.COMPLETED
        
        if not self.state_machine.can_transition(current_state, target_state):
            target_state = SessionState.CANCELLED
            if not self.state_machine.can_transition(current_state, target_state):
                return None
        
        session = await self.session_repository.update_state(
            session_id,
            target_state,
        )
        
        if self.event_bus:
            duration = None
            if session.started_at and session.ended_at:
                duration = (session.ended_at - session.started_at).total_seconds()
            
            await self.event_bus.publish(Event(
                type=EventType.SESSION_ENDED,
                source="session_service",
                session_id=session_id,
                data={
                    "session_id": session_id,
                    "reason": reason,
                    "duration": duration,
                },
            ))
        
        logger.info(f"Session ended: {session_id}, reason: {reason}")
        return SessionResponse.model_validate(session)
    
    async def send_message(
        self,
        session_id: str,
        data: MessageCreate,
    ) -> MessageResponse:
        """Send a message to the session."""
        message = await self.message_repository.create(session_id, data)
        return MessageResponse.model_validate(message)
    
    async def get_messages(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[MessageResponse]:
        """Get messages from a session."""
        messages = await self.message_repository.list_by_session(
            session_id,
            skip=skip,
            limit=limit,
        )
        return [MessageResponse.model_validate(m) for m in messages]
