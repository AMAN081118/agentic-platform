"""
Chat routes — REST endpoint only.
WebSocket is handled separately in ws_handler.py
"""

from fastapi import APIRouter, Depends
from db.models import ChatRequest, MessageCreate, SessionCreate
from db.operations import SessionOps, MessageOps
from auth.dependencies import get_optional_user
from agent.core.runner import AgentRunner
from memory.short_term import ShortTermMemory

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_optional_user),
):
    """REST chat endpoint — full agent execution, returns complete response."""
    user_id = user["id"]

    if request.session_id:
        session = SessionOps.get(request.session_id)
        if not session:
            session = SessionOps.create(
                SessionCreate(
                    user_id=user_id,
                    agent_type=request.agent,
                    title=request.message[:50],
                )
            )
    else:
        session = SessionOps.create(
            SessionCreate(
                user_id=user_id,
                agent_type=request.agent,
                title=request.message[:50],
            )
        )

    session_id = session["id"]

    MessageOps.create(
        MessageCreate(
            session_id=session_id,
            role="user",
            content=request.message,
        )
    )

    chat_history = ShortTermMemory.get_recent(session_id, limit=10)

    result = AgentRunner.run(
        message=request.message,
        agent_type=request.agent,
        session_id=session_id,
        user_id=user_id,
        chat_history=chat_history[:-1],
    )

    response_text = result["response"]

    assistant_msg = MessageOps.create(
        MessageCreate(
            session_id=session_id,
            role="assistant",
            content=response_text,
        )
    )

    SessionOps.touch(session_id)

    return {
        "agent": request.agent,
        "session_id": session_id,
        "response": response_text,
        "message_id": assistant_msg.get("id"),
        "iterations": result.get("iterations", 0),
        "latency_ms": result.get("latency_ms", 0),
        "memory_used": result.get("memory_used", False),
    }