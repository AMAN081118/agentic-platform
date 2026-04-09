"""
Memory management routes — inspect, search, and manage memories.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from auth.dependencies import get_optional_user
from memory.long_term import LongTermMemory
from memory.embeddings import EmbeddingService

router = APIRouter()


class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5
    min_similarity: float = 0.3


class MemoryStoreRequest(BaseModel):
    content: str
    session_id: str
    metadata: Optional[dict] = None


@router.post("/memory/search")
async def search_memory(
    request: MemorySearchRequest,
    user: dict = Depends(get_optional_user),
):
    """Search long-term memory by semantic similarity."""
    results = LongTermMemory.search(
        query=request.query,
        user_id=user["id"],
        top_k=request.top_k,
        min_similarity=request.min_similarity,
    )
    return {
        "query": request.query,
        "results": results,
        "count": len(results),
    }


@router.post("/memory/store")
async def store_memory(
    request: MemoryStoreRequest,
    user: dict = Depends(get_optional_user),
):
    """Manually store a memory snippet."""
    success = LongTermMemory.store(
        content=request.content,
        session_id=request.session_id,
        user_id=user["id"],
        metadata=request.metadata,
    )
    return {"stored": success}


@router.delete("/memory/{session_id}")
async def delete_session_memory(session_id: str):
    """Delete all memories for a session."""
    success = LongTermMemory.delete_by_session(session_id)
    return {"deleted": success}


@router.get("/memory/info")
async def memory_info():
    """Get embedding model info."""
    try:
        info = EmbeddingService.get_model_info()
        return {"status": "ready", **info}
    except Exception as e:
        return {"status": "not_loaded", "error": str(e)}