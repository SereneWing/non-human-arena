"""Sessions API router."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from modules.session.repositories.session_repository import (
    MessageRepository,
    ParticipantRepository,
    SessionRepository,
)
from modules.session.schemas.session import (
    MessageCreate,
    MessageResponse,
    SessionCreate,
    SessionDetailResponse,
    SessionListResponse,
    SessionResponse,
    SessionUpdate,
)
from modules.session.services.session_service import SessionService
from modules.session.services.state_machine import SessionStateMachine

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Get session service dependency."""
    session_repo = SessionRepository(db)
    message_repo = MessageRepository(db)
    participant_repo = ParticipantRepository(db)
    state_machine = SessionStateMachine()
    return SessionService(session_repo, message_repo, participant_repo, state_machine)


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    service: SessionService = Depends(get_session_service),
):
    """Create a new session."""
    return await service.create_session(data)


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SessionService = Depends(get_session_service),
):
    """List all sessions."""
    return await service.list_sessions(skip=skip, limit=limit)


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
):
    """Get session by ID."""
    session = await service.get_session_detail(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    data: SessionUpdate,
    service: SessionService = Depends(get_session_service),
):
    """Update session."""
    session = await service.update_session(session_id, data)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
):
    """Delete session."""
    success = await service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/{session_id}/start", response_model=SessionResponse)
async def start_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
):
    """Start a session."""
    session = await service.start_session(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Cannot start session")
    return session


@router.post("/{session_id}/pause", response_model=SessionResponse)
async def pause_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
):
    """Pause a session."""
    session = await service.pause_session(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Cannot pause session")
    return session


@router.post("/{session_id}/resume", response_model=SessionResponse)
async def resume_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
):
    """Resume a session."""
    session = await service.resume_session(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Cannot resume session")
    return session


@router.post("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
):
    """End a session."""
    session = await service.end_session(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Cannot end session")
    return session


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SessionService = Depends(get_session_service),
):
    """Get messages from a session."""
    return await service.get_messages(session_id, skip=skip, limit=limit)


@router.post("/{session_id}/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    session_id: str,
    data: MessageCreate,
    service: SessionService = Depends(get_session_service),
):
    """Send a message to a session."""
    return await service.send_message(session_id, data)
