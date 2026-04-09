"""
Pydantic models for request/response validation and DB row mapping.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


# ============================================
# SESSION MODELS
# ============================================

class SessionCreate(BaseModel):
    user_id: str = "anonymous"
    agent_type: str = "health"
    title: Optional[str] = "New Chat"


class SessionResponse(BaseModel):
    id: str
    user_id: str
    agent_type: str
    title: str
    created_at: str
    updated_at: str


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    agent_type: Optional[str] = None


# ============================================
# MESSAGE MODELS
# ============================================

class MessageCreate(BaseModel):
    session_id: str
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    metadata: Optional[dict] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    metadata: dict
    created_at: str


# ============================================
# CHAT REQUEST / RESPONSE
# ============================================

class ChatRequest(BaseModel):
    agent: str = "health"
    message: str
    session_id: Optional[str] = None
    user_id: str = "anonymous"


class ChatResponse(BaseModel):
    agent: str
    session_id: str
    response: str
    message_id: Optional[str] = None


# ============================================
# AUTH MODELS
# ============================================

class UserSignUp(BaseModel):
    email: str
    password: str


class UserSignIn(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    access_token: Optional[str] = None


# ============================================
# EMBEDDING MODELS
# ============================================

class EmbeddingCreate(BaseModel):
    session_id: str
    user_id: str = "anonymous"
    content: str
    embedding: list[float]
    metadata: Optional[dict] = Field(default_factory=dict)


class EmbeddingMatch(BaseModel):
    id: str
    content: str
    metadata: dict
    similarity: float


# ============================================
# AGENT LOG MODELS
# ============================================

class AgentLogCreate(BaseModel):
    session_id: str
    event_type: Literal["llm_call", "tool_call", "memory_fetch", "error"]
    agent_type: str
    input_data: Optional[dict] = Field(default_factory=dict)
    output_data: Optional[dict] = Field(default_factory=dict)
    latency_ms: int = 0