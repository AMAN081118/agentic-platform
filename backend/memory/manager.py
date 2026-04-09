"""
Memory Manager — orchestrates short-term and long-term memory.
Decides what to store, what to retrieve, and how to format context.
"""

from typing import Optional
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.embeddings import EmbeddingService
from agent.configs.base import MemoryConfig


class MemoryManager:
    """
    Central memory orchestrator.
    Combines short-term (recent messages) and long-term (RAG) memory.
    """

    @staticmethod
    def get_context(
        session_id: str,
        user_id: str,
        current_message: str,
        memory_config: MemoryConfig,
    ) -> dict:
        """
        Build complete memory context for the agent.

        Returns:
            {
                'short_term': list of recent messages,
                'long_term': list of relevant memories,
                'formatted': combined context string
            }
        """
        result = {
            "short_term": [],
            "long_term": [],
            "formatted": "",
        }

        # 1. Short-term: recent messages
        short_term = ShortTermMemory.get_recent(
            session_id=session_id,
            limit=memory_config.short_term_limit,
        )
        result["short_term"] = short_term

        # 2. Long-term: semantic search (if enabled)
        if memory_config.long_term_enabled and current_message:
            long_term = LongTermMemory.search(
                query=current_message,
                user_id=user_id,
                top_k=memory_config.long_term_top_k,
                min_similarity=0.35,
            )
            result["long_term"] = long_term

        # 3. Format combined context
        result["formatted"] = MemoryManager._format_context(
            short_term=short_term,
            long_term=result["long_term"],
        )

        return result

    @staticmethod
    def _format_context(
        short_term: list[dict],
        long_term: list[dict],
    ) -> str:
        """Format memory into a context string for the LLM."""
        parts = []

        if long_term:
            parts.append("RELEVANT MEMORIES:")
            for i, mem in enumerate(long_term, 1):
                similarity = mem.get("similarity", 0)
                content = mem.get("content", "")
                parts.append(f"  {i}. [{similarity:.0%} match] {content}")
            parts.append("")

        return "\n".join(parts) if parts else ""

    @staticmethod
    def should_store(
        content: str,
        role: str,
        memory_config: MemoryConfig,
    ) -> bool:
        """
        Decide if a message is important enough to store in long-term memory.

        Criteria:
        - Must be user or assistant message
        - Must have minimum length
        - Must not be a simple greeting or acknowledgment
        """
        if not memory_config.auto_store:
            return False

        if role not in ("user", "assistant"):
            return False

        if not content or len(content.strip()) < 20:
            return False

        # Skip simple conversational messages
        skip_patterns = [
            "hello", "hi", "hey", "thanks", "thank you",
            "bye", "goodbye", "ok", "okay", "sure",
            "yes", "no", "yeah", "nah", "got it",
        ]
        lower_content = content.strip().lower()
        if lower_content in skip_patterns:
            return False

        # Skip very short messages (likely not informative)
        word_count = len(content.split())
        if word_count < 5:
            return False

        return True

    @staticmethod
    def store_message(
        content: str,
        session_id: str,
        user_id: str,
        role: str,
        agent_type: str,
        memory_config: MemoryConfig,
    ) -> bool:
        """
        Conditionally store a message in long-term memory.

        Args:
            content: Message text
            session_id: Current session
            user_id: Current user
            role: Message role (user/assistant)
            agent_type: Current agent type
            memory_config: Memory configuration

        Returns:
            True if stored, False if skipped or failed
        """
        if not MemoryManager.should_store(content, role, memory_config):
            return False

        metadata = {
            "role": role,
            "agent_type": agent_type,
            "source": "auto_store",
        }

        return LongTermMemory.store(
            content=content,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata,
        )

    @staticmethod
    def store_conversation_summary(
        messages: list[dict],
        session_id: str,
        user_id: str,
        agent_type: str,
    ) -> bool:
        """
        Store a summary of a conversation chunk as a single memory.
        Useful for compressing long conversations into retrievable knowledge.
        """
        if not messages or len(messages) < 4:
            return False

        # Build a simple summary from the messages
        user_msgs = [m["content"] for m in messages if m["role"] == "user"]
        assistant_msgs = [m["content"] for m in messages if m["role"] == "assistant"]

        if not user_msgs:
            return False

        # Create a summary text
        topics = " | ".join(msg[:100] for msg in user_msgs[:3])
        summary = f"Conversation about: {topics}"

        if assistant_msgs:
            # Add key points from assistant
            key_points = assistant_msgs[-1][:200]
            summary += f"\nKey info provided: {key_points}"

        metadata = {
            "type": "conversation_summary",
            "agent_type": agent_type,
            "message_count": len(messages),
        }

        return LongTermMemory.store(
            content=summary,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata,
        )