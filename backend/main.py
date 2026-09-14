"""
Agentic AI Platform — Main Entry Point
"""

import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routes.health import router as health_router
from routes.chat import router as chat_router
from routes.auth import router as auth_router
from routes.sessions import router as sessions_router
from routes.memory import router as memory_router
from middleware.rate_limit import RateLimitMiddleware

app = FastAPI(
    title="Agentic AI Platform",
    description="A modular, configurable AI agent system",
    version="0.5.0",
)

# Middleware (order matters — first added = outermost)
app.add_middleware(RateLimitMiddleware, max_requests=30, window_seconds=60)
# Add CORS last so it is the outermost middleware. That ensures CORS headers
# are present even when a downstream middleware or route returns an error.
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://a2z-agents.vercel.app",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX") or None,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# REST Routes
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(sessions_router, prefix="/api", tags=["Sessions"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(memory_router, prefix="/api", tags=["Memory"])


# WebSocket — mounted directly (no prefix issues)
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    from routes.ws_handler import handle_websocket_chat
    await handle_websocket_chat(websocket)


@app.on_event("startup")
async def startup_event():
    """Warm optional services without making the HTTP server unavailable."""
    try:
        from db.supabase_client import get_supabase
        get_supabase()
        print("Supabase client initialized")
    except Exception as e:
        print(f"Supabase initialization failed: {e}")

    try:
        from agent.configs.registry import load_all_agents
        load_all_agents()

        from agent.core.graph import get_agent_graph
        get_agent_graph()
        print("Agent graph initialized")
    except Exception as e:
        print(f"Agent initialization failed: {e}")

    print("Agentic AI Platform v0.5.0 started")
    print("REST: http://localhost:8000/docs")
    print("WS:   ws://localhost:8000/ws/chat")
