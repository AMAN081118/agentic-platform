"""
Short-term memory — recent conversation messages from the current session.
"""

from db.operations import MessageOps


class ShortTermMemory:
    """Retrieve and format recent messages for context."""

    @staticmethod
    def get_recent(session_id: str, limit: int = 10) -> list[dict]:
        """
        Get the N most recent messages in a session.

        Args:
            session_id: Session to fetch from
            limit: Maximum messages to return

        Returns:
            List of {'role': str, 'content': str} dicts, oldest first
        """
        if not session_id:
            return []

        try:
            messages = MessageOps.get_recent(session_id, count=limit)
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
                if msg.get("role") in ("user", "assistant", "system")
            ]
        except Exception as e:
            print(f"Short-term memory error: {e}")
            return []

    @staticmethod
    def format_for_context(messages: list[dict], max_chars: int = 4000) -> str:
        """
        Format messages into a text block for context injection.
        Truncates from the beginning if too long.

        Args:
            messages: List of message dicts
            max_chars: Maximum character limit

        Returns:
            Formatted string of conversation history
        """
        if not messages:
            return ""

        lines = []
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            lines.append(f"{role}: {content}")

        text = "\n".join(lines)

        # Truncate from beginning if too long
        if len(text) > max_chars:
            text = "...\n" + text[-max_chars:]

        return text