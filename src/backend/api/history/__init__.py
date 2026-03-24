"""History API router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{session_id}")
async def get_session_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get session history."""
    return {"session_id": session_id, "messages": []}


@router.get("/{session_id}/export")
async def export_session_history(
    session_id: str,
    format: str = "json",
    db: AsyncSession = Depends(get_db),
):
    """Export session history."""
    return {
        "session_id": session_id,
        "format": format,
        "export_url": f"/api/v1/history/{session_id}/download",
    }
