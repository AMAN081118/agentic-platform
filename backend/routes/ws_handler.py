"""
WebSocket handler — extracted from chat.py for clean mounting.
"""

import uuid
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

from db.models import MessageCreate, SessionCreate
from db.operations import SessionOps, MessageOps
from agent.core.streaming import StreamingHandler
from agent.core.runner import AgentRunner
from agent.configs.registry import get_agent_config
from memory.short_term import ShortTermMemory
from memory.manager import MemoryManager


class WSConnectionManager:
    """Manages active WebSocket connections with health tracking."""

    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket, cid: str):
        await ws.accept()
        self.connections[cid] = ws

    def disconnect(self, cid: str):
        self.connections.pop(cid, None)

    async def send(self, cid: str, data: dict) -> bool:
        ws = self.connections.get(cid)
        if not ws:
            return False
        try:
            await ws.send_json(data)
            return True
        except Exception:
            self.disconnect(cid)
            return False

    @property
    def count(self):
        return len(self.connections)


manager = WSConnectionManager()


async def handle_websocket_chat(websocket: WebSocket):
    """
    Main WebSocket chat handler.

    Protocol:
    Client → Server:
    {"agent": "health", "message": "...", "session_id": "...", "user_id": "anonymous"}

    Server → Client:
    {"type": "connected", "client_id": "..."}
    {"type": "session", "session_id": "..."}
    {"type": "status", "content": "thinking"}
    {"type": "tool", "content": "Using calc..."}
    {"type": "token", "content": "Hello"}
    {"type": "end", "session_id": "..."}
    {"type": "error", "content": "..."}
    """
    client_id = str(uuid.uuid4())[:8]
    await manager.connect(websocket, client_id)

    try:
        # Send connection confirmation
        await manager.send(client_id, {
            "type": "connected",
            "client_id": client_id,
        })

        while True:
            # Wait for message
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=300,  # 5 min timeout
                )
            except asyncio.TimeoutError:
                await manager.send(client_id, {
                    "type": "error",
                    "content": "Connection timed out",
                })
                break

            agent_type = data.get("agent", "health")
            message = data.get("message", "").strip()
            session_id = data.get("session_id")
            user_id = data.get("user_id", "anonymous")

            if not message:
                await manager.send(client_id, {
                    "type": "error",
                    "content": "Empty message",
                })
                continue

            # === Session handling ===
            try:
                if session_id:
                    existing = SessionOps.get(session_id)
                    if not existing:
                        session_id = None

                if not session_id:
                    session = SessionOps.create(
                        SessionCreate(
                            user_id=user_id,
                            agent_type=agent_type,
                            title=message[:50],
                        )
                    )
                    session_id = session["id"]
                    await manager.send(client_id, {
                        "type": "session",
                        "session_id": session_id,
                    })
            except Exception as e:
                await manager.send(client_id, {
                    "type": "error",
                    "content": f"Session error: {str(e)}",
                })
                continue

            # === Store user message ===
            try:
                MessageOps.create(
                    MessageCreate(
                        session_id=session_id,
                        role="user",
                        content=message,
                    )
                )
            except Exception:
                pass

            # === Get context ===
            chat_history = []
            memory_context = None

            try:
                chat_history = ShortTermMemory.get_recent(session_id, limit=10)
            except Exception:
                pass

            try:
                config = get_agent_config(agent_type)
                if config.memory.long_term_enabled:
                    memory_result = MemoryManager.get_context(
                        session_id=session_id,
                        user_id=user_id,
                        current_message=message,
                        memory_config=config.memory,
                    )
                    memory_context = memory_result.get("formatted", "")
            except Exception:
                pass

            # === Stream response ===
            full_response = ""

            try:
                async for event in StreamingHandler.stream_agent_response(
                    message=message,
                    agent_type=agent_type,
                    session_id=session_id,
                    user_id=user_id,
                    chat_history=chat_history[:-1] if chat_history else [],
                    memory_context=memory_context,
                ):
                    event_type = event.get("type", "")
                    content = event.get("content", "")

                    if event_type == "token":
                        full_response += content

                    await manager.send(client_id, event)

            except Exception as e:
                # === Fallback to sync execution ===
                try:
                    result = AgentRunner.run(
                        message=message,
                        agent_type=agent_type,
                        session_id=session_id,
                        user_id=user_id,
                        chat_history=chat_history[:-1] if chat_history else [],
                    )
                    full_response = result.get("response", "Sorry, something went wrong.")

                    # Stream word by word as fallback
                    words = full_response.split()
                    for word in words:
                        await manager.send(client_id, {
                            "type": "token",
                            "content": word + " ",
                        })
                        await asyncio.sleep(0.02)

                except Exception as fallback_err:
                    full_response = "I encountered an error. Please try again."
                    await manager.send(client_id, {
                        "type": "token",
                        "content": full_response,
                    })

            # === Store assistant response ===
            if full_response.strip():
                try:
                    MessageOps.create(
                        MessageCreate(
                            session_id=session_id,
                            role="assistant",
                            content=full_response.strip(),
                        )
                    )
                except Exception:
                    pass

                # Auto-store in memory
                try:
                    config = get_agent_config(agent_type)
                    MemoryManager.store_message(
                        content=message,
                        session_id=session_id,
                        user_id=user_id,
                        role="user",
                        agent_type=agent_type,
                        memory_config=config.memory,
                    )
                    MemoryManager.store_message(
                        content=full_response.strip(),
                        session_id=session_id,
                        user_id=user_id,
                        role="assistant",
                        agent_type=agent_type,
                        memory_config=config.memory,
                    )
                except Exception:
                    pass

            try:
                SessionOps.touch(session_id)
            except Exception:
                pass

            # Send end signal
            await manager.send(client_id, {
                "type": "end",
                "session_id": session_id,
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WS error [{client_id}]: {e}")
    finally:
        manager.disconnect(client_id)