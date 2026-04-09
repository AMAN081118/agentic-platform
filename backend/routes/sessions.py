"""
Session management routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from db.models import SessionCreate, SessionUpdate
from db.operations import SessionOps, MessageOps
from auth.dependencies import get_optional_user

router = APIRouter()


@router.post("/sessions")
async def create_session(
    data: SessionCreate,
    user: dict = Depends(get_optional_user),
):
    """Create a new chat session."""
    data.user_id = user["id"]
    session = SessionOps.create(data)
    return {"session": session}


@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_optional_user)):
    """List all sessions for the current user."""
    sessions = SessionOps.list_by_user(user["id"])
    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a single session with its messages."""
    session = SessionOps.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = MessageOps.get_by_session(session_id)
    return {"session": session, "messages": messages}


@router.patch("/sessions/{session_id}")
async def update_session(session_id: str, data: SessionUpdate):
    """Update session title or agent type."""
    session = SessionOps.update(session_id, data)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session": session}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all related data."""
    success = SessionOps.delete(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True}