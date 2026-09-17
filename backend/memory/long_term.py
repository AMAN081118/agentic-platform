"""
Long-term memory — vector similarity search via pgvector in Supabase.
Stores and retrieves semantically relevant memory snippets.
"""

import time
from typing import Optional
from memory.embeddings import EmbeddingService
from db.operations import EmbeddingOps
from db.models import EmbeddingCreate, AgentLogCreate


class LongTermMemory:
    """
    Vector-based long-term memory using pgvector.
    Stores text as embeddings and retrieves by semantic similarity.
    """

    @staticmethod
    def store(
        content: str,
        session_id: str,
        user_id: str = "anonymous",
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Store a memory snippet with its embedding in Supabase.

        Args:
            content: Text to store
            session_id: Associated session
            user_id: Associated user
            metadata: Extra info (source, type, importance, etc.)

        Returns:
            True if stored successfully
        """
        if not EmbeddingService.is_enabled() or not content or not content.strip():
            return False

        try:
            start = time.time()

            # Generate embedding
            embedding = EmbeddingService.embed(content)

            # Store in Supabase
            result = EmbeddingOps.store(
                EmbeddingCreate(
                    session_id=session_id,
                    user_id=user_id,
                    content=content,
                    embedding=embedding,
                    metadata=metadata or {},
                )
            )

            latency = int((time.time() - start) * 1000)

            # Log the storage
            try:
                from db.operations import LogOps
                LogOps.create(
                    AgentLogCreate(
                        session_id=session_id,
                        event_type="memory_fetch",
                        agent_type="system",
                        input_data={"action": "store", "content_length": len(content)},
                        output_data={"stored": bool(result)},
                        latency_ms=latency,
                    )
                )
            except Exception:
                pass

            return bool(result)

        except Exception as e:
            print(f"Memory store error: {e}")
            return False

    @staticmethod
    def store_batch(
        contents: list[str],
        session_id: str,
        user_id: str = "anonymous",
        metadata: Optional[dict] = None,
    ) -> int:
        """
        Store multiple memory snippets at once (batch embedding).

        Returns:
            Number of successfully stored items
        """
        if not EmbeddingService.is_enabled() or not contents:
            return 0

        # Filter empty strings
        valid_contents = [c for c in contents if c and c.strip()]
        if not valid_contents:
            return 0

        try:
            embeddings = EmbeddingService.embed_batch(valid_contents)
            stored = 0

            for content, embedding in zip(valid_contents, embeddings):
                try:
                    EmbeddingOps.store(
                        EmbeddingCreate(
                            session_id=session_id,
                            user_id=user_id,
                            content=content,
                            embedding=embedding,
                            metadata=metadata or {},
                        )
                    )
                    stored += 1
                except Exception:
                    continue

            return stored

        except Exception as e:
            print(f"Batch memory store error: {e}")
            return 0

    @staticmethod
    def search(
        query: str,
        user_id: str = "anonymous",
        top_k: int = 3,
        min_similarity: float = 0.3,
    ) -> list[dict]:
        """
        Search for relevant memory snippets using semantic similarity.

        Args:
            query: Search query text
            user_id: Filter by user (None for all users)
            top_k: Maximum number of results
            min_similarity: Minimum cosine similarity threshold

        Returns:
            List of dicts with 'content', 'similarity', 'metadata'
        """
        if not EmbeddingService.is_enabled() or not query or not query.strip():
            return []

        try:
            start = time.time()

            # Generate query embedding
            query_embedding = EmbeddingService.embed(query)

            # Search in Supabase via pgvector
            results = EmbeddingOps.search(
                query_embedding=query_embedding,
                user_id=user_id,
                match_count=top_k,
            )

            # Filter by minimum similarity
            filtered = [
                r for r in results
                if r.get("similarity", 0) >= min_similarity
            ]

            latency = int((time.time() - start) * 1000)

            # Log the search
            try:
                from db.operations import LogOps
                LogOps.create(
                    AgentLogCreate(
                        session_id="system",
                        event_type="memory_fetch",
                        agent_type="system",
                        input_data={
                            "action": "search",
                            "query": query[:200],
                            "top_k": top_k,
                        },
                        output_data={
                            "results_count": len(filtered),
                            "top_similarity": filtered[0]["similarity"] if filtered else 0,
                        },
                        latency_ms=latency,
                    )
                )
            except Exception:
                pass

            return filtered

        except Exception as e:
            print(f"Memory search error: {e}")
            return []

    @staticmethod
    def delete_by_session(session_id: str) -> bool:
        """Delete all memories for a session."""
        try:
            return EmbeddingOps.delete_by_session(session_id)
        except Exception as e:
            print(f"Memory delete error: {e}")
            return False
