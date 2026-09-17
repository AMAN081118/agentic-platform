"""
WebSocket connection manager — handles multiple concurrent connections.
"""

from fastapi import WebSocket
from typing import Optional
import json


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Accept and register a new connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client connected: {client_id} (total: {len(self.active_connections)})")

    def disconnect(self, client_id: str) -> None:
        """Remove a connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client disconnected: {client_id} (total: {len(self.active_connections)})")

    async def send_json(self, client_id: str, data: dict) -> bool:
        """Send JSON data to a specific client."""
        ws = self.active_connections.get(client_id)
        if ws:
            try:
                await ws.send_json(data)
                return True
            except Exception:
                self.disconnect(client_id)
                return False
        return False

    async def send_token(self, client_id: str, token: str) -> bool:
        """Send a single token to a client."""
        return await self.send_json(client_id, {
            "type": "token",
            "content": token,
        })

    async def send_status(self, client_id: str, status: str) -> bool:
        """Send a status update to a client."""
        return await self.send_json(client_id, {
            "type": "status",
            "content": status,
        })

    async def send_end(self, client_id: str, session_id: str = "") -> bool:
        """Send end-of-stream signal."""
        return await self.send_json(client_id, {
            "type": "end",
            "content": "",
            "session_id": session_id,
        })

    async def send_error(self, client_id: str, error: str) -> bool:
        """Send error message."""
        return await self.send_json(client_id, {
            "type": "error",
            "content": error,
        })

    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)


# Global instance
manager = ConnectionManager()