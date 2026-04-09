"""
Database CRUD operations — clean, modular, reusable.
Each class handles one table.
"""

from typing import Optional
from db.supabase_client import get_supabase
from db.models import (
    SessionCreate,
    SessionResponse,
    SessionUpdate,
    MessageCreate,
    MessageResponse,
    EmbeddingCreate,
    EmbeddingMatch,
    AgentLogCreate,
)


class SessionOps:
    """CRUD for sessions table."""

    @staticmethod
    def create(data: SessionCreate) -> dict:
        """Create a new chat session."""
        result = (
            get_supabase()
            .table("sessions")
            .insert(
                {
                    "user_id": data.user_id,
                    "agent_type": data.agent_type,
                    "title": data.title,
                }
            )
            .execute()
        )
        return result.data[0] if result.data else {}

    @staticmethod
    def get(session_id: str) -> Optional[dict]:
        """Get a session by ID."""
        result = (
            get_supabase()
            .table("sessions")
            .select("*")
            .eq("id", session_id)
            .execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    def list_by_user(user_id: str, limit: int = 50) -> list[dict]:
        """List sessions for a user, newest first."""
        result = (
            get_supabase()
            .table("sessions")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    @staticmethod
    def update(session_id: str, data: SessionUpdate) -> Optional[dict]:
        """Update a session (title, agent_type)."""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return None

        result = (
            get_supabase()
            .table("sessions")
            .update(update_data)
            .eq("id", session_id)
            .execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    def delete(session_id: str) -> bool:
        """Delete a session (cascades to messages + embeddings)."""
        result = (
            get_supabase()
            .table("sessions")
            .delete()
            .eq("id", session_id)
            .execute()
        )
        return len(result.data) > 0

    @staticmethod
    def touch(session_id: str) -> None:
        """Update the updated_at timestamp."""
        get_supabase().table("sessions").update(
            {"updated_at": "now()"}
        ).eq("id", session_id).execute()


class MessageOps:
    """CRUD for messages table."""

    @staticmethod
    def create(data: MessageCreate) -> dict:
        """Store a new message."""
        result = (
            get_supabase()
            .table("messages")
            .insert(
                {
                    "session_id": data.session_id,
                    "role": data.role,
                    "content": data.content,
                    "metadata": data.metadata or {},
                }
            )
            .execute()
        )
        return result.data[0] if result.data else {}

    @staticmethod
    def get_by_session(
        session_id: str, limit: int = 50, order_asc: bool = True
    ) -> list[dict]:
        """Get messages for a session, ordered by time."""
        query = (
            get_supabase()
            .table("messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=not order_asc)
            .limit(limit)
        )
        result = query.execute()
        return result.data or []

    @staticmethod
    def get_recent(session_id: str, count: int = 10) -> list[dict]:
        """Get the N most recent messages (for short-term memory)."""
        result = (
            get_supabase()
            .table("messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(count)
            .execute()
        )
        # Reverse so oldest is first
        messages = result.data or []
        messages.reverse()
        return messages

    @staticmethod
    def delete_by_session(session_id: str) -> bool:
        """Delete all messages in a session."""
        result = (
            get_supabase()
            .table("messages")
            .delete()
            .eq("session_id", session_id)
            .execute()
        )
        return True


class EmbeddingOps:
    """CRUD for embeddings table (vector memory)."""

    @staticmethod
    def store(data: EmbeddingCreate) -> dict:
        """Store an embedding."""
        result = (
            get_supabase()
            .table("embeddings")
            .insert(
                {
                    "session_id": data.session_id,
                    "user_id": data.user_id,
                    "content": data.content,
                    "embedding": data.embedding,
                    "metadata": data.metadata or {},
                }
            )
            .execute()
        )
        return result.data[0] if result.data else {}

    @staticmethod
    def search(
        query_embedding: list[float],
        user_id: Optional[str] = None,
        match_count: int = 5,
    ) -> list[dict]:
        """
        Semantic search using pgvector via the match_embeddings RPC function.
        """
        params = {
            "query_embedding": query_embedding,
            "match_count": match_count,
        }
        if user_id:
            params["filter_user_id"] = user_id

        result = get_supabase().rpc("match_embeddings", params).execute()
        return result.data or []

    @staticmethod
    def delete_by_session(session_id: str) -> bool:
        """Delete all embeddings for a session."""
        get_supabase().table("embeddings").delete().eq(
            "session_id", session_id
        ).execute()
        return True


class LogOps:
    """CRUD for agent_logs table (evaluation & debugging)."""

    @staticmethod
    def create(data: AgentLogCreate) -> dict:
        """Log an agent event."""
        result = (
            get_supabase()
            .table("agent_logs")
            .insert(
                {
                    "session_id": data.session_id,
                    "event_type": data.event_type,
                    "agent_type": data.agent_type,
                    "input_data": data.input_data or {},
                    "output_data": data.output_data or {},
                    "latency_ms": data.latency_ms,
                }
            )
            .execute()
        )
        return result.data[0] if result.data else {}

    @staticmethod
    def get_by_session(session_id: str) -> list[dict]:
        """Get all logs for a session."""
        result = (
            get_supabase()
            .table("agent_logs")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .execute()
        )
        return result.data or []

    @staticmethod
    def get_by_type(event_type: str, limit: int = 100) -> list[dict]:
        """Get logs filtered by event type."""
        result = (
            get_supabase()
            .table("agent_logs")
            .select("*")
            .eq("event_type", event_type)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []